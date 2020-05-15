import asyncio
import logging
from collections import defaultdict
from upb.protocol import UPBProtocol
from upb.util import encode_register_request
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
        if self.devices.get(network_id, {}).get(device_id, None) is None:
            new_device = UPBDevice(self, network_id, device_id, logger=self.logger)
            self.devices[network_id][device_id] = new_device
        device = self.get_device(network_id, device_id)
        device.update_registers(position, data)

    async def handle_disconnect_callback(self):
        """Reconnect automatically unless stopping."""
        self.is_connected = False
        if self.disconnect_callback:
            self.disconnect_callback()
        if self.reconnect:
            self.logger.debug("Protocol disconnected...reconnecting")
            await self.setup()

    async def update_registers(self, network, device, register_len=256):
        """Fetch registers from device."""
        index = 0
        while index < register_len:
            start = index
            remaining = register_len - index
            if remaining >= 16:
                req_len = 16
            else:
                req_len = remaining
            packet = encode_register_request(network, device, start, req_len)
            response = await self.protocol.send_packet(packet)
            assert(response['setup_register'] == start)
            index += len(response['register_val'])

    async def get_registers(self, network, device, register_len=256):
        await self.update_registers(network, device, register_len)
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