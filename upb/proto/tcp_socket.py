import asyncio
import logging
from pprint import pformat
from binascii import hexlify, unhexlify
from collections import deque
from struct import pack, unpack

from upb.const import UpbMessage, UpbTransmission, PimCommand, UpbReg, \
    MdidSet, MdidCoreCmd, MdidDeviceControlCmd, MdidCoreReport, \
    UPB_MESSAGE_TYPE, UPB_MESSAGE_PIMREPORT_TYPE, INITIAL_PIM_REG_QUERY_BASE
from upb.util import cksum, hexdump


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
        self.buffer = b''
        self.message_buffer = b''

    def write_packet(self, packet):
        self.transport.write(packet)

    def connection_made(self, transport):
        self.transport = transport
        if self.pulse.handle_connect_callback:
            self.pulse.handle_connect_callback()

    def data_received(self, data):
        self.buffer += data
        while b'\r' in self.buffer:
            line, self.buffer = self.buffer.split(b'\r', 1)
            if len(line) > 1:
                self.pulse.line_received(line)

    def connection_lost(self, *args):
        if self.pulse.handle_disconnect_callback:
            self.pulse.handle_disconnect_callback()
