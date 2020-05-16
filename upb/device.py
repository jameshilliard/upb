from upb.util import hexdump
from upb.register import UPBMemory

from pprint import pformat

class UPBDevice:

    def __init__(self, client, network_id, device_id, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.client = client
        self.protocol = client.protocol
        self.network_id = network_id
        self.device_id = device_id
        self.registers = bytearray(256)
        self.reg = UPBMemory.from_buffer(self.registers)

    def __repr__(self):
        '''Returns representation of the object'''
        return(f"{self.__class__.__name__}(UPBMemory={self.reg!r})")

    @property
    def network(self):
        return self.reg.net_id

    @property
    def device(self):
        return self.reg.module_id

    @property
    def password(self):
        return self.reg.password

    async def sync_registers(self):
        await self.client.update_registers(self.network_id, self.device_id)

    def update_registers(self, pos, data):
        self.registers[pos:pos + len(data)] = data
        self.logger.debug(f"Device {self.network_id}:{self.device_id} registers: \n{hexdump(self.registers)}")
        self.logger.debug(f"Device {self.network_id}:{self.device_id}: {pformat(dict(self.reg))}")
