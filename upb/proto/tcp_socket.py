import asyncio


class UPBTCPProto(asyncio.Protocol):

    def __init__(self, pulse=None, loop=None, logger=None):
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self._cmd_timeout = None
        self.pulse = pulse
        self.pulse.protocol = self

    def write_packet(self, packet):
        self.transport.write(packet)

    def connection_made(self, transport):
        self.transport = transport
        if self.pulse.handle_connect_callback:
            self.pulse.handle_connect_callback()

    def data_received(self, data):
        self.pulse.upb_data_received(data)

    def connection_lost(self, *args):
        if self.pulse.handle_disconnect_callback:
            self.pulse.handle_disconnect_callback()
