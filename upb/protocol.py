import asyncio
import logging
from pprint import pformat
from binascii import unhexlify
from collections import deque
from struct import unpack

from upb.const import UpbMessage, UpbTransmission, PimCommand, \
    MdidSet, MdidCoreCmd, MdidDeviceControlCmd, MdidCoreReport, \
    UPB_MESSAGE_TYPE, UPB_MESSAGE_PIMREPORT_TYPE, INITIAL_PIM_REG_QUERY_BASE
from upb.util import cksum, hexdump


class UPBProtocol(asyncio.Protocol):

    def __init__(self, client=None, loop=None, logger=None, disconnect_callback=None,
        register_callback=None, signature_callback = None):
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.client = client
        self.disconnect_callback = disconnect_callback
        self.register_callback = register_callback
        self.signature_callback = signature_callback
        self.server_transport = None
        self.buffer = b''
        self.last_command = {}
        self.message_buffer = b''
        self.pim_accept = False
        self.transmitted = False
        self.upb_packet = bytearray(64)
        self.pulse_data_seq = 0
        self.packet_byte = 0
        self.packet_crumb = 0
        self.waiters = deque()
        self.active_transaction = None
        self.active_packet = None
        self.in_transaction = False

    async def send_packet(self, packet):
        packet = await self._send_packet(packet)
        return packet

    def _send_packet(self, packet):
        """Add packet to send queue."""
        fut = self.loop.create_future()
        self.waiters.append((fut, packet))
        self._send_next_packet()
        return fut

    def _process_received_packet(self, packet):
        if self.in_transaction:
            self.active_transaction.set_result(packet)
            self.active_transaction = None
            self.in_transaction = False
            self.active_packet = None

    def _send_next_packet(self):
        """Write next packet in send queue."""
        assert(self.packet_byte == 0)
        assert(self.pulse_data_seq == 0)
        assert(self.packet_crumb == 0)
        self.set_state_zero()
        if self.waiters and self.in_transaction is False:
            waiter, packet = self.waiters.popleft()
            self.logger.debug(f'sending packet: {packet}')
            self.active_transaction = waiter
            self.in_transaction = True
            self.active_packet = packet
            self.transport.write(packet + b'\r')

    def connection_made(self, transport):
        self.logger.debug("connected to PIM")
        self.connected = True
        self.transport = transport

    def set_state_zero(self):
        self.transmitted = False
        self.pulse_data_seq = 0
        self.packet_crumb = 0
        self.packet_byte = 0

    def process_packet(self, packet):
        self.logger.debug(f"Got upb message data: {hexdump(packet)}")
        control_word = packet[0:2]
        data_len = (control_word[0] & 0x1f) - 6
        transmit_cnt = control_word[1] & 0x0c >> 2
        transmit_seq = control_word[1] & 0x03
        network_id = packet[2]
        destination_id = packet[3]
        source_id = packet[4]
        mdid_set = MdidSet(packet[5] & 0xe0)
        if mdid_set == MdidSet.MDID_CORE_COMMANDS:
            mdid_cmd = MdidCoreCmd(packet[5] & 0x1f)
        elif mdid_set == MdidSet.MDID_DEVICE_CONTROL_COMMANDS:
            mdid_cmd = MdidDeviceControlCmd(packet[5] & 0x1f)
        elif mdid_set == MdidSet.MDID_CORE_REPORTS:
            mdid_cmd = MdidCoreReport(packet[5] & 0x1f)
        crc = packet[data_len + 5]
        computed_crc = cksum(packet[0:data_len + 5])
        if crc != computed_crc:
            self.logger.error(f"crc: {crc} != computed_crc: {computed_crc}")
        response = {
            'transmit_cnt': transmit_cnt,
            'transmit_seq': transmit_seq,
            'network_id': network_id,
            'destination_id': destination_id,
            'device_id': source_id,
            'mdid_set': mdid_set,
            'mdid_cmd': mdid_cmd
        }
        if mdid_cmd == MdidCoreReport.MDID_DEVICE_CORE_REPORT_REGISTERVALUES:
            setup_register = packet[6]
            register_val = packet[7:data_len + 5]
            response['setup_register'] = setup_register
            response['register_val'] = register_val
            self.register_callback(network_id, source_id, setup_register, register_val)
            self._process_received_packet(response)
        elif mdid_cmd == MdidCoreReport.MDID_DEVICE_CORE_REPORT_DEVICESIGNATURE:
            signature = packet[6:data_len + 5]
            random_number = unpack('>H', packet[6:8])[0]
            device_signal = packet[8]
            device_noise = packet[9]
            id_checksum = unpack('>H', packet[10:12])[0]
            setup_checksum = unpack('>H', packet[12:14])[0]
            ct_bytes = packet[14]
            if ct_bytes == 0:
                ct_bytes = 256
            diagnostic = packet[15:23]
            response['random_number'] = random_number
            response['device_signal'] = device_signal
            response['device_noise'] = device_noise
            response['id_checksum'] = id_checksum
            response['setup_checksum'] = setup_checksum
            response['ct_bytes'] = ct_bytes
            response['diagnostic'] = diagnostic
            self.signature_callback(network_id, source_id, id_checksum, setup_checksum, ct_bytes)
            self._process_received_packet(response)
        elif mdid_cmd == MdidCoreReport.MDID_DEVICE_CORE_REPORT_SETUPTIME:
            setup_mode_register = packet[6]
            setup_mode_timer = packet[7]
            response['setup_mode_register'] = setup_mode_register
            response['setup_mode_timer'] = setup_mode_timer
            self._process_received_packet(response)
            self._send_next_packet()
        else:
            response['data'] = packet[6:data_len + 5]
        self.logger.debug(pformat(response))

    def process_transmitted(self, data):
        mystery_header = data[0]
        packet = data[1:]
        control_word = packet[0:2]
        data_len = (control_word[0] & 0x1f) - 6
        transmit_cnt = control_word[1] & 0x0c >> 2
        transmit_seq = control_word[1] & 0x03
        network_id = packet[2]
        destination_id = packet[3]
        source_id = packet[4]
        mdid_set = MdidSet(packet[5] & 0xe0)
        if mdid_set == MdidSet.MDID_CORE_COMMANDS:
            mdid_cmd = MdidCoreCmd(packet[5] & 0x1f)
        elif mdid_set == MdidSet.MDID_DEVICE_CONTROL_COMMANDS:
            mdid_cmd = MdidDeviceControlCmd(packet[5] & 0x1f)
        elif mdid_set == MdidSet.MDID_CORE_REPORTS:
            mdid_cmd = MdidCoreReport(packet[5] & 0x1f)
        crc = packet[data_len + 5]
        computed_crc = cksum(packet[0:data_len + 5])
        if crc != computed_crc:
            self.logger.error(f"crc: {crc} != computed_crc: {computed_crc}")
        response = {
            'transmit_cnt': transmit_cnt,
            'transmit_seq': transmit_seq,
            'network_id': network_id,
            'destination_id': destination_id,
            'device_id': source_id,
            'mdid_set': mdid_set,
            'mdid_cmd': mdid_cmd
        }
        if mdid_cmd == MdidCoreCmd.MDID_CORE_COMMAND_STARTSETUP:
            password = unpack('>H', packet[6:8])[0]
            response['password'] = password
            self._process_received_packet(response)
            self._send_next_packet()
        self.logger.debug(pformat(response))
        self.logger.debug(f'pim transmitted packet: {hexdump(packet)}, with mystery_header: {hex(mystery_header)}')


    def line_received(self, line):
        if UpbMessage.has_value(line[UPB_MESSAGE_TYPE]):
            command = UpbMessage(line[UPB_MESSAGE_TYPE])
            data = line[1:]
            if command != UpbMessage.UPB_MESSAGE_IDLE and \
            command != UpbMessage.UPB_MESSAGE_TRANSMITTED and \
            not UpbMessage.is_message_data(command):
                self.logger.debug(f"PIM {command.name} data: {data}")
            if command == UpbMessage.UPB_MESSAGE_IDLE:
                if self.in_transaction:
                    self.logger.debug(f"Received PIM idle data: {data}")
                self._send_next_packet()
            elif command == UpbMessage.UPB_MESSAGE_DROP:
                self.logger.debug('dropped message')
                self.set_state_zero()
            elif command == UpbMessage.UPB_MESSAGE_PIMREPORT:
                self.logger.debug(f"got pim report: {hex(line[UPB_MESSAGE_PIMREPORT_TYPE])} with len: {len(line)}")
                if len(line) > UPB_MESSAGE_PIMREPORT_TYPE:
                    transmission = UpbTransmission(line[UPB_MESSAGE_PIMREPORT_TYPE])
                    self.logger.debug(f"transmission: {transmission.name}")
                    if transmission == UpbTransmission.UPB_PIM_REGISTERS:
                        register_data = unhexlify(line[UPB_MESSAGE_PIMREPORT_TYPE + 1:])
                        start = register_data[0]
                        register_val = register_data[1:]
                        self.logger.debug(f"start: {hex(start)} register_val: {register_val}")
                        if start == INITIAL_PIM_REG_QUERY_BASE:
                            self.logger.debug("got pim in initial phase query mode")
                    elif transmission == UpbTransmission.UPB_PIM_ACCEPT:
                        self.pim_accept = True
                        self.logger.debug("got pim accept")
                else:
                    self.logger.debug(f'got corrupt pim report: {hex(line[UPB_MESSAGE_PIMREPORT_TYPE])} with len: {len(line)}')

            elif command == UpbMessage.UPB_MESSAGE_SYNC:
                self.packet_byte = 0
                self.packet_crumb = 0
            elif command == UpbMessage.UPB_MESSAGE_START:
                self.packet_byte = 0
                self.packet_crumb = 0
            elif UpbMessage.is_message_data(command):
                if len(data) == 2:
                    seq = unhexlify(b'0' + data[1:2])[0]
                    two_bits = command.value - 0x30
                    assert(seq == self.pulse_data_seq)
                    if seq == self.pulse_data_seq:
                        if self.packet_crumb == 0:
                            self.upb_packet[self.packet_byte] = (two_bits << 6)
                            self.packet_crumb += 1
                        elif self.packet_crumb == 1:
                            self.upb_packet[self.packet_byte] |= (two_bits << 4)
                            self.packet_crumb += 1
                        elif self.packet_crumb == 2:
                            self.upb_packet[self.packet_byte] |= (two_bits << 2)
                            self.packet_crumb += 1
                        elif self.packet_crumb == 3:
                            self.upb_packet[self.packet_byte] |= two_bits
                            self.packet_crumb = 0
                            self.packet_byte += 1
                        self.pulse_data_seq += 1
                        if self.pulse_data_seq > 0x0f:
                            self.pulse_data_seq = 0
                    else:
                        self.logger.debug(f"Got upb message data bad seq: {hex(self.seq)}")

            elif command == UpbMessage.UPB_MESSAGE_TRANSMITTED:
                self.transmitted = True
                if len(data) == 2:
                    seq = unhexlify(b'0' + data[1:2])[0]
                    two_bits = data[0] - 0x30
                    assert(seq == self.pulse_data_seq)
                    if seq == self.pulse_data_seq:
                        if self.packet_crumb == 0:
                            self.upb_packet[self.packet_byte] = (two_bits << 6)
                            self.packet_crumb += 1
                        elif self.packet_crumb == 1:
                            self.upb_packet[self.packet_byte] |= (two_bits << 4)
                            self.packet_crumb += 1
                        elif self.packet_crumb == 2:
                            self.upb_packet[self.packet_byte] |= (two_bits << 2)
                            self.packet_crumb += 1
                        elif self.packet_crumb == 3:
                            self.upb_packet[self.packet_byte] |= two_bits
                            self.packet_crumb = 0
                            self.packet_byte += 1
                        self.pulse_data_seq += 1
                        if self.pulse_data_seq > 0x0f:
                            self.pulse_data_seq = 0
                    else:
                        self.logger.debug(f"Got upb message data bad seq: {hex(self.seq)}")
            elif command == UpbMessage.UPB_MESSAGE_ACK or command == UpbMessage.UPB_MESSAGE_NAK:
                if self.transmitted:
                    self.message_buffer = bytes(self.upb_packet[0:self.packet_byte])
                    self.set_state_zero()
                    if len(self.message_buffer) != 0:
                        self.process_transmitted(self.message_buffer)
                else:
                    self.message_buffer = bytes(self.upb_packet[0:self.packet_byte])
                    self.set_state_zero()
                    if len(self.message_buffer) != 0:
                        self.process_packet(self.message_buffer)
                if len(self.message_buffer) != 0:
                    if self.last_command.get('mdid_cmd', None) == MdidCoreCmd.MDID_CORE_COMMAND_GETDEVICESIGNATURE:
                        self.logger.debug(f"Decoding signature with length {len(self.message_buffer)}")
                        for index in range(len(self.message_buffer)):
                            self.logger.debug(f"Reg index: {index}, value: {hex(self.message_buffer[index])}")
                self.message_buffer = b''
                if self.packet_byte > 0:
                    self.set_state_zero()
        else:
            self.logger.debug(f'PIM failed to parse line: {hexdump(line)}')

    def data_received(self, data):
        self.buffer += data
        while b'\r' in self.buffer:
            line, self.buffer = self.buffer.split(b'\r', 1)
            if len(line) > 1:
                self.line_received(line)
        if self.server_transport:
            self.server_transport.write(data)

    def connection_lost(self, *args):
        self.connected = False
