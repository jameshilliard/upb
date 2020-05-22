import asyncio
import logging
from collections import defaultdict
from struct import unpack
from upb.protocol import UPBProtocol
from upb.util import cksum, hexdump, encode_register_request, encode_signature_request, encode_startsetup_request, encode_setuptime_request
from upb.device import UPBDevice

class UPBClient:

    def __init__(self, host, port=2101, disconnect_callback=None,
                 reconnect_callback=None, loop=None, logger=None,
                 timeout=10, reconnect_interval=10):
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
        self.transport = None
        self.protocol = None
        self.is_connected = False
        self.reconnect = True
        self.timeout = timeout
        self.reconnect_interval = reconnect_interval
        self.disconnect_callback = disconnect_callback
        self.reconnect_callback = reconnect_callback
        self.devices = defaultdict(dict)

    async def setup(self):
        """Set up the connection with automatic retry."""
        while True:
            fut = self.loop.create_connection(
                lambda: UPBProtocol(
                    self,
                    disconnect_callback=self.handle_disconnect_callback,
                    register_callback=self.handle_register_update,
                    signature_callback=self.handle_signature_update,
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
                self.is_connected = True
                if self.reconnect_callback:
                    self.reconnect_callback()
                break
            await asyncio.sleep(self.reconnect_interval)

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
        response = await self.protocol.send_packet(packet)
        return response['id_checksum'], response['setup_checksum'], response['ct_bytes']

    async def get_setup_time(self, network, device):
        packet = encode_setuptime_request(network, device)
        response = await self.protocol.send_packet(packet)
        return response

    async def test_password(self, network, device, password):
        packet = encode_startsetup_request(network, device, password)
        response = await self.protocol.send_packet(packet)
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
        while index < ct_bytes:
            start = index
            remaining = ct_bytes - index
            if remaining >= 16:
                req_len = 16
            else:
                req_len = remaining
            packet = encode_register_request(network, device, start, req_len)
            response = await self.protocol.send_packet(packet)
            assert(response['setup_register'] == start)
            index += len(response['register_val'])
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
            if upbid_diff > 256:
                password_test[0] = upbid_diff - 256
                password_test[1] = 256
            else:
                password_test[1] = upbid_diff
            while password_test[0] <= 256:
                password_int = unpack('>H', password_test)[0]
                self.logger.info(f"trying password = {password_int}")
                good_password = await self.test_password(network, device, password_int)
                if good_password:
                    packet = encode_register_request(network, device, 2, 2)
                    response = await self.protocol.send_packet(packet)
                    pw_register = unpack('>H', response['register_val'])[0]
                    assert(pw_register == password_int)
                    break
                else:
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
                                reconnect_interval=None):
    """Create UPB Client class."""
    client = UPBClient(host, port=port,
                        disconnect_callback=disconnect_callback,
                        reconnect_callback=reconnect_callback,
                        loop=loop, logger=logger,
                        timeout=timeout, reconnect_interval=reconnect_interval)
    await client.setup()

    return client