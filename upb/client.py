import asyncio
import logging
from pprint import pformat
from collections import defaultdict
from struct import unpack
from upb.const import UpbReg
from upb.pulse import UPBPulse
from upb.util import cksum, hexdump, encode_register_request, encode_signature_request, encode_startsetup_request, encode_setuptime_request
from upb.device import UPBDevice
from upb.proto.tcp_socket import UPBTCPProto
from upb.proto.pulseworx_gateway import PulseworxGatewayProto

class UPBClient:

    def __init__(self, host, port=2101, disconnect_callback=None,
                 reconnect_callback=None, loop=None, logger=None,
                 timeout=10, reconnect_interval=10,
                 username=None, password=None):
        """Initialize the UPB client wrapper."""
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.transport = None
        self.protocol = None
        self.pulse = None
        self.is_connected = False
        self.reconnect = True
        self.timeout = timeout
        self.reconnect_interval = reconnect_interval
        self.disconnect_callback = disconnect_callback
        self.reconnect_callback = reconnect_callback
        self.devices = defaultdict(dict)
        if self.username is not None and self.password is not None:
            self.proto_type = "pulseworx_gateway"
        else:
            self.proto_type = "tcp_socket"

    async def setup(self):
        """Set up the connection with automatic retry."""
        while True:
            self.pulse = UPBPulse(
                register_callback=self.handle_register_update,
                signature_callback=self.handle_signature_update,
                disconnect_callback=self.handle_disconnect_callback,
                logger=self.logger)
            self.logger.info(f"proto_type: {self.proto_type}")
            if self.proto_type == "pulseworx_gateway":
                fut = self.loop.create_connection(
                    lambda: PulseworxGatewayProto(
                        self.pulse,
                        username=self.username, password=self.password,
                        loop=self.loop, logger=self.logger),
                    host=self.host,
                    port=self.port)
            elif self.proto_type == "tcp_socket":
                fut = self.loop.create_connection(
                    lambda: UPBTCPProto(
                        self.pulse,
                        loop=self.loop, logger=self.logger),
                    host=self.host,
                    port=self.port)
            try:
                self.transport, self.protocol = \
                    await asyncio.wait_for(fut, timeout=self.timeout)
            except asyncio.TimeoutError:
                self.logger.warning("Could not connect due to timeout error.")
            except OSError as exc:
                self.logger.warning("Could not connect due to error: %s",
                                    str(exc))
            else:
                if self.proto_type == "pulseworx_gateway":
                    await self.protocol.authenticate()
                    await self.protocol.client_stop_pulse()
                self.is_connected = True
                await self.pim_init()
                if self.proto_type == "pulseworx_gateway":
                    await self.protocol.client_start_pulse()
                if self.reconnect_callback:
                    self.reconnect_callback()
                break
            await asyncio.sleep(self.reconnect_interval)

    async def pim_init(self):
        pim_info = await self.pim_info()
        self.logger.debug(pformat(pim_info))
        result = await self.pim_set_mode()

    async def pim_info(self):
        info = {}
        info['firmware_version'] = await self.pim_get_firmware_version()
        info['mode'] = await self.pim_get_mode()
        info['manufacturer'] = await self.pim_get_manufacturer()
        info['network'] = await self.pim_get_network()
        info['product'] = await self.pim_get_product()
        info['options'] = await self.pim_get_options()
        info['pulse'] = (info['options'] & 0x02) == 0
        info['upb_version'] = await self.pim_get_upb_version()
        info['noisefloor'] = await self.pim_get_noisefloor()
        return info

    async def pim_set_mode(self):
        mode = await self.pulse.pim_memory_write(UpbReg.UPB_REG_PIMOPTIONS, 0xf0)
        return mode

    async def pim_get_firmware_version(self):
        version = await self.pulse.pim_memory_read(UpbReg.UPB_REG_FIRMWAREVERSION)
        return version

    async def pim_get_mode(self):
        mode = await self.pulse.pim_memory_read(UpbReg.UPB_REG_PIMOPTIONS)
        return mode[0]

    async def pim_get_network(self):
        network = await self.pulse.pim_memory_read(UpbReg.UPB_REG_NETWORKID)
        return network

    async def pim_get_manufacturer(self):
        manufacturer = await self.pulse.pim_memory_read(UpbReg.UPB_REG_MANUFACTURERID)
        return manufacturer

    async def pim_get_product(self):
        product = await self.pulse.pim_memory_read(UpbReg.UPB_REG_PRODUCTID)
        return product

    async def pim_get_options(self):
        options = await self.pulse.pim_memory_read(UpbReg.UPB_REG_UPBOPTIONS)
        return options[0]

    async def pim_get_upb_version(self):
        upb_version = await self.pulse.pim_memory_read(UpbReg.UPB_REG_UPBVERSION)
        return upb_version[0]

    async def pim_get_noisefloor(self):
        noisefloor = await self.pulse.pim_memory_read(UpbReg.UPB_REG_NOISEFLOOR)
        return noisefloor[0]

    def stop(self):
        """Shut down transport."""
        self.reconnect = False
        self.logger.debug("Shutting down.")
        if self.transport:
            self.transport.close()

    def get_device(self, network_id, device_id):
        if self.devices.get(network_id, {}).get(device_id, None) is None:
            self.devices[network_id][device_id] = \
                UPBDevice(self, network_id, device_id, logger=self.logger)
        return self.devices[network_id][device_id]

    def handle_register_update(self, network_id, device_id, position, data):
        """Receive register update."""
        device = self.get_device(network_id, device_id)
        device.update_registers(position, data)

    def handle_signature_update(self, network_id, device_id, id_checksum, setup_checksum, ct_bytes):
        """Receive register signature update."""
        device = self.get_device(network_id, device_id)
        device.update_signature(id_checksum, setup_checksum, ct_bytes)

    async def handle_disconnect_callback(self):
        """Reconnect automatically unless stopping."""
        self.is_connected = False
        if self.disconnect_callback:
            self.disconnect_callback()
        if self.reconnect:
            self.logger.debug("Protocol disconnected...reconnecting")
            await self.setup()

    async def update_signature(self, network, device):
        """Fetch register signature from device."""
        packet = encode_signature_request(network, device)
        response = await self.pulse.send_packet(packet)
        return response['id_checksum'], response['setup_checksum'], response['ct_bytes']

    async def get_setup_time(self, network, device):
        packet = encode_setuptime_request(network, device)
        response = await self.pulse.send_packet(packet)
        return response

    async def test_password(self, network, device, password):
        packet = encode_startsetup_request(network, device, password)
        response = await self.pulse.send_packet(packet)
        assert(response['password'] == password)
        setup_time = await self.get_setup_time(network, device)
        if setup_time['setup_mode_timer'] != 0:
            return True
        return False

    async def update_registers(self, network, device):
        """Fetch registers from device."""
        index = 0
        upbid_crc = 0
        setup_crc = 0
        id_checksum, setup_checksum, ct_bytes = await self.update_signature(network, device)
        tasks = []
        while index < ct_bytes:
            start = index
            remaining = ct_bytes - index
            if remaining >= 16:
                req_len = 16
            else:
                req_len = remaining
            packet = encode_register_request(network, device, start, req_len)
            response = asyncio.ensure_future(self.pulse.send_packet(packet))
            tasks.append(response)
            index += req_len
        await asyncio.gather(*tasks)
        upbid_crc = sum(self.get_device(network, device).registers[0:64])
        setup_crc = sum(self.get_device(network, device).registers[0:ct_bytes])
        self.logger.debug(f"id_checksum: {id_checksum}, setup_checksum: {setup_checksum}, upbid_crc: {upbid_crc}, setup_crc: {setup_crc}")
        upbid_diff = id_checksum - upbid_crc
        setup_diff = setup_checksum - setup_crc
        assert(upbid_diff == setup_diff)
        if upbid_diff != 0:
            assert(upbid_diff <= 512)
            self.logger.info(f"password diff = {upbid_diff}")
            password_test = bytearray(2)
            # Start with numeric only guesses if diff is < checksum for password = 9999
            if upbid_diff > 306:
                numeric_only = False
            else:
                numeric_only = True
            got_numeric = False
            if numeric_only:
                low_bits = upbid_diff % 16
                high_bits = (upbid_diff - low_bits) // 16
                shifted = False
                # fill out low bits first (9+9) - 16 = 2
                if low_bits <= 2 and high_bits > 0:
                    low_bits += 16
                    high_bits -= 1
                if low_bits > 9:
                    password_test[0] = low_bits - 9
                    password_test[1] = 9
                else:
                    password_test[1] = low_bits
                if high_bits > 9:
                    password_test[0] |= ((high_bits - 9) << 4)
                    password_test[1] |= (9 << 4)
                else:
                    password_test[1] |= (high_bits << 4)
                while True:
                    password_sum = password_test[0] + password_test[1]
                    assert(password_sum == upbid_diff)
                    low_tested = False
                    while low_tested == False:
                        self.logger.info(f"trying password = {hexdump(password_test, sep='')}")
                        good_password = await self.test_password(network, device, password_test)
                        if good_password:
                            packet = encode_register_request(network, device, 2, 2)
                            response = await self.pulse.send_packet(packet)
                            pw_register = response['register_val']
                            assert(pw_register == password_test)
                            got_numeric = True
                            break
                        else:
                            # check if low bits are fully shifted
                            if (password_test[0] & 0xf) == 9 or (password_test[1] & 0xf) == 0:
                                # set flag when all low bits are tested so that we shift high bits left
                                low_tested = True
                            # shift low bits left
                            else:
                                password_test[0] += 1
                                password_test[1] -= 1
                    else:
                        # high bits fully maxed out, end numeric search
                        if ((password_test[0] & 0xf0) >> 4) == 9 and ((password_test[1] & 0xf0) >> 4) == 9:
                            break
                        # check if high bits are fully shifted left
                        elif ((password_test[0] & 0xf0) >> 4) == 9 or ((password_test[1] & 0xf0) >> 4) == 0:
                            low_sum = (password_test[0] & 0xf) + (password_test[1] & 0xf)
                            # check if we can shift a low bit to a high bit
                            if low_sum >= 16:
                                # push high bits right to reset the high bit search
                                if ((password_test[0] & 0xf0) >> 4) > 0 or ((password_test[1] & 0xf0) >> 4) < 9:
                                    to_shift = (9 - ((password_test[1] & 0xf0) >> 4)) * 16
                                    password_test[0] -= to_shift
                                    password_test[1] += to_shift
                                low_remainder = low_sum - 9
                                # try to shift low bits to high right
                                if ((password_test[1] & 0xf0) >> 4) < 9:
                                    password_test[0] -= 9
                                    password_test[1] += (16 - low_remainder)
                                # shift low bits to high left
                                else:
                                    # 16 - 9 = 7
                                    password_test[0] += 7
                                    password_test[1] -= low_remainder
                            # no low bits to shift, end numberic search
                            else:
                                break
                        # shift high bits left
                        else:
                            password_test[0] += 16
                            password_test[1] -= 16
                            # push low bits right
                            if (password_test[0] & 0xf) > 0 or (password_test[1] & 0xf) < 9:
                                to_shift = 9 - (password_test[1] & 0xf)
                                password_test[0] -= to_shift
                                password_test[1] += to_shift
                        continue
                    break

            if got_numeric == False:
                if upbid_diff > 0xff:
                    password_test[0] = upbid_diff - 0xff
                    password_test[1] = 0xff
                else:
                    password_test[0] = 0
                    password_test[1] = upbid_diff
                while password_test[0] <= 0xff:
                    if (password_test[0] & 0xf0) >> 4 <= 9 and \
                    (password_test[0] & 0xf) <= 9 and \
                    (password_test[1] & 0xf0) >> 4 <= 9 and \
                    (password_test[1] & 0xf) <= 9:
                        is_numeric = True
                    else:
                        is_numeric = False
                    if not is_numeric:
                        self.logger.info(f"trying password = {hexdump(password_test, sep='')}")
                        good_password = await self.test_password(network, device, password_test)
                        if good_password:
                            packet = encode_register_request(network, device, 2, 2)
                            response = await self.pulse.send_packet(packet)
                            pw_register = response['register_val']
                            assert(pw_register == password_test)
                            break
                    password_test[0] += 1
                    password_test[1] -= 1
        self.logger.info(f"got good password = {hexdump(self.get_device(network, device).registers[2:4], sep='')}")

    async def get_registers(self, network, device):
        await self.update_registers(network, device)
        return bytes(self.get_device(network, device).registers)

async def create_upb_connection(port=None, host=None,
                                disconnect_callback=None,
                                reconnect_callback=None, loop=None,
                                logger=None, timeout=None,
                                reconnect_interval=10, username=None, password=None):
    """Create UPB Client class."""
    client = UPBClient(host, port=port,
                        disconnect_callback=disconnect_callback,
                        reconnect_callback=reconnect_callback,
                        loop=loop, logger=logger,
                        timeout=timeout, reconnect_interval=reconnect_interval,
                        username=username, password=password)
    await client.setup()

    return client