import asyncio
import hmac
from pprint import pformat
from collections import deque
from upb.util import cksum, hexdump
from upb.const import GatewayCmd
from binascii import unhexlify
from functools import reduce
from struct import pack, unpack


class PulseworxGatewayProto(asyncio.Protocol):

    def __init__(self, pulse, username, password, loop=None, logger=None):
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self._nt_cmd_timeout = None
        self._gw_cmd_timeout = None
        self.pulse = pulse
        self.pulse_waiter = None
        self.username = username
        self.password = password
        self.pulse.protocol = self
        self.buffer = bytearray()
        self.in_transaction = False
        self.gw_cmd = None
        self.active_packet = None
        self.in_flight = None
        self.wrapped = False
        self.waiters = deque()
        self.gw_waiters = deque()
        self.auth_task = None
        self.challenge = None
        self.pim_info = {}

    def _reset_nt_cmd_timeout(self):
        """Reset timeout for command execution."""
        if self._nt_cmd_timeout:
            self._nt_cmd_timeout.cancel()
        self._nt_cmd_timeout = self.loop.call_later(10, self._resend_nt_packet)

    def _resend_nt_packet(self):
        """Write next packet in send queue."""
        packet = self.active_packet
        self.logger.warning(f'resending packet due to timeout: {hexdump(packet)}')
        self.transport.write(packet)
        self.write_gateway(cmd, packet)
        self._reset_nt_cmd_timeout()

    async def send_nt_packet(self, packet):
        fut = await self._send_nt_packet(packet)
        return fut

    def _send_nt_packet(self, packet):
        """Add packet to send queue."""
        fut = self.loop.create_future()
        self.waiters.append((fut, packet))
        self._send_next_nt_packet()
        return fut

    def _send_next_nt_packet(self):
        """Write next packet in send queue."""
        if self.waiters and self.in_transaction is False and self.in_flight is None:
            waiter, packet = self.waiters.popleft()
            self.in_flight = waiter
            self.in_transaction = True
            self.active_packet = packet
            msg = packet + b'\x00'
            self.logger.debug(f'sending nt packet: {hexdump(msg)}, msg: {msg}')
            self.transport.write(msg)
            self._reset_nt_cmd_timeout()

    def _reset_gw_cmd_timeout(self):
        """Reset timeout for command execution."""
        if self._gw_cmd_timeout:
            self._gw_cmd_timeout.cancel()
        self._gw_cmd_timeout = self.loop.call_later(10, self._resend_gw_packet)

    def _resend_gw_packet(self):
        """Write next packet in send queue."""
        cmd = self.gw_cmd
        packet = self.active_packet
        self.logger.warning(f'resending gw packet due to timeout: {hexdump(packet)}, msg: {packet}, cmd: {cmd}')
        self.write_gateway(cmd, packet)
        self._reset_gw_cmd_timeout()

    async def send_gw_packet(self, cmd, packet):
        fut = await self._send_gw_packet(cmd, packet)
        return fut

    def _send_gw_packet(self, cmd, packet):
        """Add packet to send queue."""
        fut = self.loop.create_future()
        self.gw_waiters.append((fut, cmd, packet))
        self._send_next_gw_packet()
        return fut

    def _send_next_gw_packet(self):
        """Write next packet in send queue."""
        if self.gw_waiters and self.in_transaction is False and self.in_flight is None:
            waiter, cmd, packet = self.gw_waiters.popleft()
            self.gw_cmd = cmd
            self.in_flight = waiter
            self.in_transaction = True
            self.active_packet = packet
            self.write_gateway(cmd, packet)
            self._reset_gw_cmd_timeout()

    def _handle_gw_response(self, cmd, packet):
        if cmd == GatewayCmd.SERIAL_MESSAGE.value:
            if len(packet) > 0:
                self.pulse.line_received(packet[:-1])
        elif self.in_transaction and self.gw_cmd:
            self.logger.info(f"received gateway packet: {packet}, hex: {hexdump(packet)} length: {len(packet)}, cmd: {hex(cmd)}")
            self._gw_cmd_timeout.cancel()
            self.in_transaction = False
            self.in_flight.set_result(packet)
            self.in_flight = None
            self.gw_cmd = None


    async def _client_hello(self):
        line = await self.send_nt_packet(b'UPStart/8.3.4/1')
        self.logger.info(f"line: {line}")
        errors = {
            'MAX CONNECTIONS REACHED',
            'PULSE MODE ACTIVE',
            'PIM NOT INITIALIZED',
            'FIRMWARE CORRUPT - FLASH WITH UPSTART'
        }
        if line in errors or len(line) < 12:
            self.logger.warning(f"unhandled error: {line}")
            return
        prefix, version, protocol, auth, challenge = line.split(b'/', maxsplit=4)
        majorVersion, minorVersion = version.split(b'.', maxsplit=1)
        self.pim_info = {
            'prefix': prefix,
            'version': version,
            'protocol': protocol,
            'auth': auth,
            'majorVersion': majorVersion,
            'minorVersion': minorVersion
        }
        self.challenge = unhexlify(challenge)
        self.logger.info(f'self.pim_info:\n{pformat(self.pim_info)}')

    async def _client_send_auth(self):
        if self.pim_info.get('auth', None) == b'AUTH REQUIRED':
            user = self.username.encode('utf-8')
            digest = hmac.new(self.password.encode('utf-8'), self.challenge, 'md5').hexdigest().swapcase().encode('ascii')
            line = await self.send_nt_packet(user + b'/' + digest)
            result, client = line.split(b'/', maxsplit=1)
            if result == b'AUTHENTICATION FAILED':
                self.logger.info("auth failed")
            elif result == b'AUTH SUCCEEDED':
                self.logger.info("auth succeded")
                self.wrapped = True
                self._nt_cmd_timeout.cancel()
                if self.pulse.handle_connect_callback:
                    self.pulse.handle_connect_callback()
            else:
                self.logger.info(f"unexpected auth result: {result}")

    async def client_start_pulse(self):
        cmd = GatewayCmd.START_PULSE_MODE
        timeout = 60
        response = await self.send_gw_packet(cmd, timeout)
        self.logger.info(f"start pulse response: {response}, hex: {hexdump(response)}")

    async def client_stop_pulse(self):
        cmd = GatewayCmd.EXIT_PULSE_MODE
        response = await self.send_gw_packet(cmd, b'')
        self.logger.info(f"stop pulse response: {response}, hex: {hexdump(response)}")

    async def authenticate(self):
        await self._client_hello()
        await self._client_send_auth()

    def nt_line_received(self, line):
        self.logger.info(f'pim null terminated line: {line}, hex: {hexdump(line)}')
        if self.in_transaction:
            self.in_transaction = False
            self.in_flight.set_result(line)
            self.in_flight = None

    def write_packet(self, packet):
        assert(self.wrapped)
        cmd = GatewayCmd.SEND_TO_SERIAL
        self.write_gateway(cmd, packet)

    def write_gateway(self, cmd, packet):
        assert(self.wrapped)
        if isinstance(packet, int):
            length = 1
        else:
            length = len(packet)
        gtw_pkt = bytearray(length + 4)
        gtw_pkt[0] = cmd
        gtw_pkt[1:3] = pack('>H', length)
        gtw_pkt[3 : length + 3] = packet
        gtw_pkt[length + 3] = cksum(gtw_pkt) -1
        self.logger.info(f"sent gateway packet: {gtw_pkt}, hex: {hexdump(gtw_pkt)} length: {length}")
        self.transport.write(gtw_pkt)

    def connection_made(self, transport):
        self.logger.info("pulseworx gateway connected")
        self.wrapped = False
        self.transport = transport

    def data_received(self, data):
        self.buffer += data
        if self.wrapped:
            if len(self.buffer) >= 4:
                length = unpack('>H', self.buffer[1:3])[0]
                if len(self.buffer) >= length + 4:
                    cmd = self.buffer[0]
                    packet = bytes(self.buffer[3:length + 3])
                    self.logger.info(f"cmd: {hex(cmd)}, packet: {packet}, hex: {hexdump(packet)}, cksum: {hex(self.buffer[length + 3])}")
                    #cksum = self.buffer[length + 3]
                    #comp_cksum = cksum(self.buffer[0:length + 3])
                    #self.logger.info(f"cksum = {cksum}, comp_cksum = {comp_cksum}")
                    self._handle_gw_response(cmd, packet)
                    self.buffer = self.buffer[length+4:]
        else:
            while b'\x00' in self.buffer:
                line, self.buffer = self.buffer.split(b'\x00', 1)
                if len(line) > 0:
                    self.nt_line_received(bytes(line))

    def connection_lost(self, *args):
        self.wrapped = False
        if self.pulse.handle_disconnect_callback:
            self.pulse.handle_disconnect_callback()
