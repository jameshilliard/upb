import asyncio
import logging
from upb.protocol import UPBProtocol
from upb.util import encode_register_request

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

    async def setup(self):
        """Set up the connection with automatic retry."""
        while True:
            fut = self.loop.create_connection(
                lambda: UPBProtocol(
                    self,
                    disconnect_callback=self.handle_disconnect_callback,
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

    async def handle_disconnect_callback(self):
        """Reconnect automatically unless stopping."""
        self.is_connected = False
        if self.disconnect_callback:
            self.disconnect_callback()
        if self.reconnect:
            self.logger.debug("Protocol disconnected...reconnecting")
            await self.setup()

    async def get_registers(self, network, device, register_len=256):
        """Fetch registers from device."""
        registers = bytearray()
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
            registers.extend(response['register_val'])

        return bytes(registers)

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