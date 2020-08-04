import asyncio
import hmac
from pprint import pformat
from collections import deque
from upb.util import hexdump
from binascii import unhexlify


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
        self.pulse = pulse
        self.username = username
        self.password = password
        self.pulse.protocol = self
        self.buffer = b''
        self.message_buffer = b''
        self.in_transaction = False
        self.in_flight = None
        self.wrapped = False
        self.waiters = deque()
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
        msg = packet + b'\x00'
        self.logger.warning(f'resending packet due to timeout: {hexdump(packet)}, msg: {msg}')
        self.write_packet(msg)
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
            self.logger.debug(f'sending nt packet: {hexdump(packet)}, msg: {msg}')
            self.transport.write(msg)
            self._reset_nt_cmd_timeout()

    async def _client_hello(self):
        line = await self.send_nt_packet(b'UPStart/8.3.4/1')
        print(f"line: {line}")
        errors = {
            'MAX CONNECTIONS REACHED',
            'PULSE MODE ACTIVE',
            'PIM NOT INITIALIZED',
            'FIRMWARE CORRUPT - FLASH WITH UPSTART'
        }
        if line in errors or len(line) < 12:
            print(f"unhandled error: {line}")
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
        print(f'self.pim_info:\n{pformat(self.pim_info)}')

    async def _client_send_auth(self):
        if self.pim_info.get('auth', None) == b'AUTH REQUIRED':
            user = self.username.encode('utf-8')
            digest = hmac.new(self.password.encode('utf-8'), self.challenge, 'md5').hexdigest().swapcase().encode('ascii')
            line = await self.send_nt_packet(user + b'/' + digest)
            print(f"line: {line}")

    async def authenticate(self):
        await self._client_hello()
        await self._client_send_auth()

    def nt_line_received(self, line):
        print(f'pim null terminated line: {line}, hex: {hexdump(line)}')
        if self.in_transaction:
            self.in_transaction = False
            self.in_flight.set_result(line)
            self.in_flight = None

    def write_packet(self, packet):
        self.transport.write(packet)

    def connection_made(self, transport):
        self.wrapped = False
        self.transport = transport
        #if self.pulse.handle_connect_callback:
            #self.pulse.handle_connect_callback()

    def data_received(self, data):
        self.buffer += data
        while b'\x00' in self.buffer:
            line, self.buffer = self.buffer.split(b'\x00', 1)
            if len(line) > 0:
                self.nt_line_received(line)

    def connection_lost(self, *args):
        self.wrapped = False
        if self.pulse.handle_disconnect_callback:
            self.pulse.handle_disconnect_callback()
