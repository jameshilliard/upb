from struct import unpack
from enum import Enum
from ctypes import Structure, BigEndianStructure, c_uint8, c_uint16, c_uint32, c_ubyte, c_char, Array

class Dictionary:
    # Implement the iterator method such that dict(...) results in the correct
    # dictionary.
    def __iter__(self):
        for k, t in self._fields_:
            if (issubclass(t, Structure)):
                yield (k, dict(getattr(self, k)))
            else:
                yield (k, getattr(self, k))

    # Implement the reverse method, with some special handling for dict's and
    # lists.
    def from_dict(self, dict_object):
        for k, t in self._fields_:
            set_value = dict_object[k]
            if (isinstance(set_value, dict)):
                v = t()
                v.from_dict(set_value)
                setattr(self, k, v)
            elif (isinstance(set_value, list)):
                v = getattr(self, k)
                for j in range(0, len(set_value)):
                    v[j] = set_value[j]
                setattr(self, k, v)
            else:
                setattr(self, k, set_value)

    def __str__(self):
        return str(dict(self))

class UPBMemory(BigEndianStructure, Dictionary):
    _pack_ = 1
    _fields_ = [('net_id', c_uint8),
                ('module_id', c_uint8),
                ('password', c_uint16),
                ('upb_options', c_uint8),
                ('upb_version', c_uint8),
                ('manufacturer_id', c_uint16),
                ('product_id', c_uint16),
                ('firmware_major_version', c_uint8),
                ('firmware_minor_version', c_uint8),
                ('serial_number', c_uint32),
                ('network_name', c_char * 16),
                ('room_name', c_char * 16),
                ('device_name', c_char * 16)]

    def __get_value_str(self, name, fmt='{}'):
        val = getattr(self, name)
        if isinstance(val, Array):
            val = list(val)
        return fmt.format(val)

    def __repr__(self):
        return '{name}({fields})'.format(
                name = self.__class__.__name__,
                fields = ', '.join(
                    '{}={}'.format(name, self.__get_value_str(name, '{!r}')) for name, _ in self._fields_)
                )