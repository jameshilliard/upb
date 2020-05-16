from upb.util import hexdump
from upb.register import UPBID, get_register_map
from upb.memory import *

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
        self.upbid = UPBID.from_buffer(self.registers)

    def __repr__(self):
        '''Returns representation of the object'''
        return(f"{self.__class__.__name__}(UPBMemory={self.upbid!r})")

    @property
    def reg(self):
        reg_class = get_register_map(self.product)
        if reg_class is None:
            return self.upbid
        return reg_class.from_buffer(self.registers)

    @property
    def network(self):
        return self.upbid.net_id

    @property
    def device(self):
        return self.upbid.module_id

    @property
    def manufacturer(self):
        return UPBManufacturerID(self.upbid.manufacturer_id)

    @property
    def product(self):
        if self.manufacturer == UPBManufacturerID.SimplyAutomated:
            return SAProductID(self.upbid.product_id)
        else:
            return self.upbid.product_id

    @property
    def password(self):
        return self.upbid.password

    async def sync_registers(self):
        await self.client.update_registers(self.network_id, self.device_id)

    def update_registers(self, pos, data):
        self.registers[pos:pos + len(data)] = data
        self.logger.debug(f"Device {self.network_id}:{self.device_id} registers: \n{hexdump(self.registers)}")
        self.logger.debug(f"Device {self.network_id}:{self.device_id}: {pformat(dict(self.reg))}")
        self.logger.debug(f"manufacturer = {self.manufacturer.name}, product = {self.product.name}")
