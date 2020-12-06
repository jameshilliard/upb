from struct import unpack
from enum import Enum
from ctypes import Structure, BigEndianStructure, c_uint8, c_uint16, c_uint32, c_ubyte, c_char, Array
from collections import defaultdict

from upb.memory import *

class Dictionary:
    # Implement the iterator method such that dict(...) results in the correct
    # dictionary.
    def __iter__(self):
        ignored = {'reserved1', 'reserved2', 'reserved3', 'reserved4', 'reserved5'}
        subtypes = (RockerAction, UPBButtonAction, UPBIndicator, UPBInput, IOMInput, TimedEvent, ESIComponent)
        for k, v in self._fields_:
            t = getattr(self, k)
            if k not in ignored:
                if isinstance(v, type) and issubclass(v, UPBID):
                    sk = getattr(self, k)
                    for nk, nt in getattr(self, k):
                        yield (nk, getattr(self, nk))
                elif isinstance(v, type) and issubclass(v, subtypes):
                    nd = defaultdict(dict)
                    for nk, nv in t._fields_:
                        nt = getattr(t, nk)
                        nd[nk] = nt
                    yield (k, dict(nd))
                elif isinstance(v, type) and issubclass(v, Array):
                    ak = getattr(self, k)
                    al = []
                    for av in ak:
                        if isinstance(type(av), type) and issubclass(type(av), subtypes):
                            nd = defaultdict(dict)
                            for nk, nv in av._fields_:
                                nd[nk] = getattr(av, nk)
                            al.append(dict(nd))
                        else:
                            al.append(av)
                    yield (k, al)
                else:
                    yield (k, t)

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

class UPBID(BigEndianStructure, Dictionary):
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

# Switch: PCS WS1
class UPBSwitch(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids', c_uint8 * 16), # 0x40
        ('preset_level_table', c_uint8 * 16), # 0x50
        ('preset_fade_table', c_uint8 * 16), # 0x60
        ('top_rocker_tid', c_uint8), # 0x70
        ('top_rocker_single_click', c_uint8),
        ('top_rocker_double_click', c_uint8),
        ('top_rocker_hold', c_uint8),
        ('top_rocker_release', c_uint8),
        ('bottom_rocker_tid', c_uint8), # 0x75
        ('bottom_rocker_single_click', c_uint8),
        ('bottom_rocker_double_click', c_uint8),
        ('bottom_rocker_hold', c_uint8),
        ('bottom_rocker_release', c_uint8),
        ('top_rocker_sc_level', c_uint8), # 0x7a
        ('top_rocker_sc_rate', c_uint8),
        ('top_rocker_dc_level', c_uint8),
        ('top_rocker_dc_rate', c_uint8),
        ('bottom_rocker_sc_level', c_uint8), # 0x7e
        ('bottom_rocker_sc_rate', c_uint8),
        ('bottom_rocker_dc_level', c_uint8),
        ('bottom_rocker_dc_rate', c_uint8),
        ('reserved1', c_char * 6),
        ('min_dim_level', c_uint8), # 0x88 HAI ONLY!
        ('auto_off_link', c_uint8), # 0x89
        ('auto_off_cmd', c_uint8), # 0x8a
        ('led_options', c_uint8), # 0x8b LED Control
        ('switch_options', c_uint8), # 0x8c WS2: barGraphOption, WS1L: min dim level
        ('default_options', c_uint8), # 0x8d Dim options
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('timed_options', c_uint8), # 0x8f
        ('reserved2', c_char * 112)
    ]

# 1 Channel Module
class UPBModule(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids', c_uint8 * 16),
        ('preset_level_table', c_uint8 * 16),
        ('preset_fade_table', c_uint8 * 16),
        ('reserved1', c_char * 23),
        ('lts_link', c_uint8), # 0x87
        ('lts_cmd', c_uint8), # 0x88
        ('auto_off_link', c_uint8), # 0x89
        ('auto_off_cmd', c_uint8), # 0x8a
        ('led_options', c_uint8), # 0x8b LED Control
        ('options', c_uint8), # 0x8c Options for pid 7. Min Dim Level for pid 9
        ('default_options', c_uint8), # 0x8d Dim & other options
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('timed_options', c_uint8), # Auto Shutoff time
        ('reserved3', c_char * 112)
    ]

# 2 Channel Module
class UPBModule2(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids_1', c_uint8 * 16),
        ('preset_level_table_1', c_uint8 * 16),
        ('preset_fade_table_1', c_uint8 * 16),
        ('link_ids_2', c_uint8 * 16),
        ('preset_level_table_2', c_uint8 * 16),
        ('preset_fade_table_2', c_uint8 * 16),
        ('default_options', c_uint8), # 0xa0 Options
        ('transmission_options', c_uint8), # 0xa1 Transmission options
        ('led_options', c_uint8), # 0xa2 LED Control
        ('options', c_uint8), # 0xa3 Min dim level
        ('transmit_link', c_uint8), # 0xa4
        ('transmit_cmd', c_uint8), # 0xa5
        ('transmit_link_2', c_uint8), # 0xa6
        ('transmit_cmd_2', c_uint8), # 0xa7
        ('reserved2', c_char * 24),
        ('timed_options_1', c_uint8), # 0xc0
        ('timed_options_2', c_uint8), # 0xc1
        ('timed_options_3', c_uint8), # 0xc2
        ('timed_options_4', c_uint8), # 0xc3
        ('auto_off_link_1', c_uint8), # 0xc4
        ('auto_off_cmd_1', c_uint8), # 0xc5
        ('auto_off_link_2', c_uint8), # 0xc6
        ('auto_off_cmd_2', c_uint8), # 0xc7
        ('reserved4', c_char * 56)
    ]

class UPBButtonAction(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('link', c_uint8),
        ('single_click', c_uint8),
        ('double_click', c_uint8),
        ('hold', c_uint8),
        ('release', c_uint8)
    ]

class UPBIndicator(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('link', c_uint8),
        ('preset1', c_uint8),
        ('preset2', c_uint8)
    ]

# Keypad
class UPBKeypad(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('indicator_links', c_uint8 * 8), # indicators by group
        ('button_action_table', UPBButtonAction * 8),
        ('led_group_table', c_uint8 * 8), # indicators by group
        ('reserved1', c_char * 18),
        ('use_options', c_uint8), # 0x8a mode of keypad use 0/FF=5-Scene + Dim/Brt, 1=6-Scene, 2=5-Load + Dim/Brt, 3= 6-Load
        ('reserved2', c_char), # 0x8b
        ('ir_options', c_uint8), # 0x8c IR Control
        ('led_options', c_uint8), # 0x8d LED Control
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('indicator_options', c_uint8), # 0x8f For 4.14 and earlier
        ('reserved3', c_char * 48),
        ('indicator_table', UPBIndicator * 16), # indicators by mask
        ('reserved4', c_char * 16)
    ]

class UPBKeypadDimmer(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids', c_uint8 * 16),
        ('preset_level_table', c_uint8 * 16),
        ('preset_fade_table', c_uint8 * 16),
        ('indicator_table', UPBIndicator * 16),
        ('button_action_table', UPBButtonAction * 8),
        ('reserved1', c_char * 42),
        ('min_dim_level', c_uint8), # 0xf2
        ('use_options', c_uint8), # 0xf3 mode of keypad use
        ('reserved2', c_char), # 0xf4
        ('led_options', c_uint8), # 0xF5 LED Control
        ('dim_options', c_uint8), # 0xF6
        ('chirp_options', c_uint8), # 0xF7
        ('transmission_options', c_uint8), # 0xF8
        ('transmission_enable', c_uint8), # 0xF9
        ('auto_off_time', c_uint8), # 0xFA
        ('auto_off_link', c_uint8), # 0xFB
        ('auto_off_cmd', c_uint8), # 0xFC
        ('reserved3', c_char * 3)
    ]

class UPBInput(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('open_link_id', c_uint8),
        ('open_cmd_id', c_uint8),
        ('close_link_id', c_uint8),
        ('close_cmd_id', c_uint8)
    ]

# Input control module
class UPBICM(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # 4.20 Firmware or greater
        #    A1, C1, A2, C2 are link Ids
        #    B1, D1, B2, C2 are levels
        # Older firmware:
        #    A1, B1 are link ids
        #    all other are reserved
        ('input_control_a1', c_uint8),
        ('input_control_b1', c_uint8),
        ('input_control_c1', c_uint8),
        ('input_control_d1', c_uint8),
        ('input_control_a2', c_uint8),
        ('input_control_b2', c_uint8),
        ('input_control_c2', c_uint8),
        ('input_control_d2', c_uint8),
        ('reserved1', c_char * 8),
        ('input', UPBInput * 2),
        ('reserved2', c_char * 49),
        ('transmit_timeout', c_uint8), # 0x89 VIM: Transmit timeout
        ('transmit_attempts', c_uint8), # 0x8a VIM: Transmit attempts
        ('led_options', c_uint8), # 0x8b LED Control
        ('input_debounce_count', c_uint8), # 0x8c debounce
        ('reserved3', c_char),
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('heartbeat_period', c_uint8), # 0x8f VIM
        ('reserved4', c_char * 112)
    ]

class RockerAction(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('top_rocker_tid', c_uint8),
        ('top_rocker_single_click', c_uint8),
        ('top_rocker_double_click', c_uint8),
        ('top_rocker_hold', c_uint8),
        ('top_rocker_release', c_uint8),
        ('bottom_rocker_tid', c_uint8),
        ('bottom_rocker_single_click', c_uint8),
        ('bottom_rocker_double_click', c_uint8),
        ('bottom_rocker_hold', c_uint8),
        ('bottom_rocker_release', c_uint8)
    ]

# SA USQ
class UPBUSQ(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids', c_uint8 * 16), # 0x40
        ('preset_level_table', c_uint8 * 16), # 0x50
        ('preset_fade_table', c_uint8 * 16), # 0x60
        ('rocker1', RockerAction), # 0x70
        ('top_rocker_sc_level', c_uint8), # 0x7a
        ('top_rocker_sc_rate', c_uint8),
        ('top_rocker_dc_level', c_uint8),
        ('top_rocker_dc_rate', c_uint8),
        ('bottom_rocker_sc_level', c_uint8),
        ('bottom_rocker_sc_rate', c_uint8),
        ('bottom_rocker_dc_level', c_uint8),
        ('bottom_rocker_dc_rate', c_uint8),
        ('reserved2', c_char * 8),
        ('tap_options', c_uint8), # 0x8a
        ('led_options', c_uint8), # 0x8b LED Control
        ('rocker_config', c_uint8), # 0x8c Mask for rockers/buttons present in variant
        ('default_options', c_uint8), # 0x8d Options
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('rocker_options', c_uint8), # 0x8f flags and variant
        ('reserved3', c_char * 58),
        ('rocker_2_to_4', RockerAction * 3),
        ('reserved4', c_char * 24)
    ]

# SA US4
class UPBUS4(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('reserved1', c_char * 32),
        ('rockers', RockerAction * 4),
        ('dim_options_1', c_uint8), # 0x88
        ('dim_options_2', c_uint8), # 0x89
        ('dim_options_3', c_uint8), # 0x8a
        ('dim_options_4', c_uint8), # 0x8b
        ('led_options', c_uint8), # 0x8c LED Control
        ('button_config', c_uint8), # 0x8d Mask for rockers/buttons present in variant
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('variant_options', c_uint8), # 0x8f variant
        ('misc_options', c_uint8), # 0x90 state report, add/del facility, et.
        ('button_transmit_options', c_uint8), # 0x91 mask for what transmits
        ('output_options', c_uint8), # 0x92 # dimmers
        ('reserved2', c_char * 3),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids_1', c_uint8 * 8),
        ('preset_level_table_1', c_uint8 * 8),
        ('preset_fade_table_1', c_uint8 * 8),
        ('link_ids_2', c_uint8 * 8),
        ('preset_level_table_2', c_uint8 * 8),
        ('preset_fade_table_2', c_uint8 * 8),
        ('link_ids_3', c_uint8 * 8),
        ('preset_level_table_3', c_uint8 * 8),
        ('preset_fade_table_3', c_uint8 * 8),
        ('link_ids_4', c_uint8 * 8),
        ('preset_level_table_4', c_uint8 * 8),
        ('preset_fade_table_4', c_uint8 * 8),
        ('reserved3', c_char * 10)
    ]

# SA US22
class UPBUS22(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('reserved1', c_char * 32),
        ('rockers', RockerAction * 4),
        ('dim_options_1', c_uint8), # 0x88
        ('dim_options_2', c_uint8), # 0x89
        ('reserved2', c_char * 2), # 0x8a - 0x8b
        ('led_options', c_uint8), # 0x8c LED Control
        ('button_config', c_uint8), # 0x8d Mask for rockers/buttons present in variant
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('variant_options', c_uint8), # 0x8f variant, add/del facility, long body bit
        ('misc_options', c_uint8), # 0x90 state report
        ('button_transmit_options', c_uint8), # 0x91 mask for what transmits
        ('output_options', c_uint8), # 0x92 # dimmers. Always 2
        ('reserved3', c_char * 3),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids_1', c_uint8 * 16),
        ('preset_level_table_1', c_uint8 * 16),
        ('preset_fade_table_1', c_uint8 * 16),
        ('link_ids_2', c_uint8 * 16),
        ('preset_level_table_2', c_uint8 * 16),
        ('preset_fade_table_2', c_uint8 * 16),
        ('reserved4', c_char * 10)
    ]

# SA US2-40
class UPBUS2(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('link_ids', c_uint8 * 16),
        ('preset_level_table', c_uint8 * 16),
        ('preset_fade_table', c_uint8 * 16),
        ('reserved1', c_char * 26),
        ('rocker_transmit_options', c_uint8), # 0x8a
        ('led_options', c_uint8), # 0x8b LED Control
        ('rocker_config', c_uint8), # 0x8c
        ('dim_options', c_uint8), # 0x8d
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('rocker_options', c_uint8), # 0x8f rocker options and variant
        ('rocker_action', RockerAction * 4),
        ('reserved2', c_char * 72)
    ]

# SA UFQ20
class UPBUFQ(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('button_action_table', UPBButtonAction * 4),
        ('reserved1', c_char * 55),
        ('led_options', c_uint8), # 0x8b LED Control
        ('reserved2', c_char * 2),
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('reserved3', c_char),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids_1', c_uint8 * 8),
        ('preset_level_table_1', c_uint8 * 8),
        ('preset_fade_table_1', c_uint8 * 8),
        ('link_ids_2', c_uint8 * 8),
        ('preset_level_table_2', c_uint8 * 8),
        ('preset_fade_table_2', c_uint8 * 8),
        ('link_ids_3', c_uint8 * 8),
        ('preset_level_table_3', c_uint8 * 8),
        ('preset_fade_table_3', c_uint8 * 8),
        ('link_ids_4', c_uint8 * 8),
        ('preset_level_table_4', c_uint8 * 8),
        ('preset_fade_table_4', c_uint8 * 8),
        ('reserved4', c_char * 2),
        ('timeout_enables', c_uint8), # 0xf2
        ('timeout_1', c_uint8),
        ('timeout_2', c_uint8),
        ('timeout_3', c_uint8),
        ('timeout_4', c_uint8),
        ('variant_options', c_uint8),
        ('reserved5', c_char * 8)
    ]

class IOMInput(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('close_link_id', c_uint8),
        ('close_cmd', c_uint8),
        ('close_b1', c_uint8),
        ('close_b2', c_uint8),
        ('open_link_id', c_uint8),
        ('open_cmd', c_uint8),
        ('open_b1', c_uint8),
        ('open_b2', c_uint8)
    ]

# WMT 3 input and 2 output module
class UPBIOM(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids_1', c_uint8 * 16),
        ('state_1', c_uint8 * 16), # 0: open 1: closed
        ('unused_1', c_uint8 * 16),
        ('link_ids_2', c_uint8 * 16),
        ('state_2', c_uint8 * 16),
        ('unused_2', c_uint8 * 16),
        ('input', IOMInput * 3),
        ('reserved1', c_char * 8),
        ('transmission_options', c_uint8), # 0xc0 Transmission options
        ('led_options', c_uint8), # 0xc1 LED Control
        ('reserved2', c_char), # 0xc2
        ('device_options', c_uint8), # 0xc3
        ('reserved3', c_char * 60)
    ]

# Fixture relay
class UPBFR(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids', c_uint8 * 16), # 0x40
        ('preset_level_table', c_uint8 * 16), # 0x50
        ('preset_fade_table', c_uint8 * 16), # 0x60
        ('rocker', RockerAction), # 0x70
        ('top_rocker_sc_level', c_uint8), # 0x7aI'll come by 4:00 +
        ('top_rocker_sc_rate', c_uint8),
        ('top_rocker_dc_level', c_uint8),
        ('top_rocker_dc_rate', c_uint8),
        ('bottom_rocker_sc_level', c_uint8),
        ('bottom_rocker_sc_rate', c_uint8),
        ('bottom_rocker_dc_level', c_uint8),
        ('bottom_rocker_dc_rate', c_uint8),
        ('reserved1', c_char * 8),
        ('tap_options', c_uint8), # 0x8a
        ('led_options', c_uint8), # 0x8b LED Control
        ('reserved2', c_char), # 0x8c
        ('output_options', c_uint8), # 0x8d Options
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('rocker_options', c_uint8), # 0x8f flags and variant
        ('reserved3', c_char * 112)
    ]

# SA USM
class UPBUSM(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('rocker1', RockerAction),
        ('rocker2', RockerAction),
        ('reserved1', c_char * 46),
        ('calib_0', c_uint8), # 0x82
        ('calib_1', c_uint8), # 0x83
        ('calib_2', c_uint8), # 0x84
        ('calib_3', c_uint8), # 0x85
        ('reserved2', c_char * 4),
        # USMR1
        # <= 1.07
        # 0x8c: byte1  rockerOptions
        # 0x8d: byte2  transmissionOptions
        # 0x8e: byte3  reserved
        #
        # >= 1.08 (or USM2)
        # 0x8c: byte1  reserved
        # 0x8d: byte2  rockerOptions
        # 0x8e: byte3  transmissionOptions
        ('rocker_transmit', c_uint8), # 0x8a
        ('led_options', c_uint8), # 0x8b LED Control
        ('byte_1', c_uint8), # 0x8c
        ('byte_2', c_uint8), # 0x8d
        ('byte_3', c_uint8), # 0x8e
        ('calib_scale', c_uint8), # 0x8f
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_ids_1', c_uint8 * 8),
        ('preset_level_table_1', c_uint8 * 8),
        ('preset_fade_table_1', c_uint8 * 8),
        ('link_ids_2', c_uint8 * 8),
        ('preset_level_table_2', c_uint8 * 8),
        ('preset_fade_table_2', c_uint8 * 8),
        ('reserved4', c_char * 64)
    ]

class DSTDate(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('start_month', c_uint8),
        ('start_day', c_uint8),
        ('end_month', c_uint8),
        ('end_day', c_uint8)
    ]

class TECFlash(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('clock', c_uint8 * 8), # 0x100
        ('jan_1_sunrise_hours', c_uint8), # 0x108
        ('jan_1_sunrise_minutes', c_uint8),
        ('jan_1_sunset_hours', c_uint8), # 0x10a
        ('jan_1_sunset_minutes', c_uint8),
        ('dst_start_month', c_uint8), # 0x10c  Current year
        ('dst_start_day', c_uint8),
        ('dst_stop_month', c_uint8), # 0x10e
        ('dst_stop_day', c_uint8),
        ('suntime_table', c_uint8 * 366), # 0x110
        ('dst_table', DSTDate * 30) # 0x300  [0] = 2006
    ]

class TimedEvent(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('time1', c_uint8),
        ('time2', c_uint8),
        ('minute', c_uint8),
        ('vary', c_uint8),
        ('transmit_link', c_uint8),
        ('transmit_cmd', c_uint8),
        ('receive_link', c_uint8),
        ('receive_level', c_uint8)
    ]

# TEC
class UPBTEC(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('led_options', c_uint8), # 0x40 LED Control
        ('transmission_options', c_uint8), # 0x41 Transmission options
        ('reserved1', c_char * 5),
        ('ct_events_in_use', c_uint8),
        ('event_table', TimedEvent * 20),
        ('reserved2', c_char * 24)
    ]

class ESIComponent(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('link_id', c_uint8),
        ('cm_msg', c_uint8),
        ('msg', c_uint8 * 7)
    ]

# ESI
class UPBESI(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('rct', ESIComponent * 16),
        ('reserved1', c_char * 16),
        ('transmission_options', c_uint8), # 0xe0 Transmission options
        ('led_options', c_uint8), # 0xe1 LED Control
        ('reserved2', c_char * 30)
    ]

# Alarm Panel Interface (API)
class UPBAPI(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        ('house_code_map', c_uint8 * 16),
        ('command_map', c_uint8 * 16),
        ('reserved1', c_char * 46),
        ('transmission_options', c_uint8), # 0x8e Transmission options
        ('reserved2', c_char * 113)
    ]

# PCS RFI
class UPBRFI(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [
        ('upbid', UPBID),
        # Not stored in this manner but as triplets.  Does take up
        # the same number of bytes
        ('link_id', c_uint8 * 32),
        ('scdc', c_uint8 * 32),
        ('hold_release', c_uint8 * 32),
        ('remote_type', c_uint8 * 32), # A1 to A7
        ('name_update', c_uint8), # A8
        ('reserved1', c_char * 2),
        ('led_options', c_uint8), # 0xab LED Control
        ('reserved2', c_char * 2),
        ('transmission_options', c_uint8), # 0xae
        ('reserved3', c_char * 49),
        ('remote_1_id', c_uint8 * 4),
        ('remote_2_id', c_uint8 * 4),
        ('remote_3_id', c_uint8 * 4),
        ('remote_4_id', c_uint8 * 4),
        ('remote_5_id', c_uint8 * 4),
        ('remote_6_id', c_uint8 * 4),
        ('remote_7_id', c_uint8 * 4),
        ('remote_8_id', c_uint8 * 4)
    ]

def get_register_map(product):
    if product in UPBKindSwitch:
        return UPBSwitch
    elif product in UPBKindModule1:
        return UPBModule
    elif product in UPBKindModule2:
        return UPBModule2
    elif product in UPBKindKeypad:
        return UPBKeypad
    elif product in UPBKindKeypadDimmer:
        return UPBKeypadDimmer
    elif product in UPBKindInput:
        return UPBICM
    elif product in UPBKindUSQ:
        return UPBUSQ
    elif product in UPBKindUS4:
        return UPBUS4
    elif product in UPBKindUS22:
        return UPBUS22
    elif product in UPBKindUS2:
        return UPBUS2
    elif product in UPBKindUFQ:
        return UPBUFQ
    elif product in UPBKindIOM:
        return UPBIOM
    elif product in UPBKindFR:
        return UPBFR
    elif product in UPBKindUSM1:
        return UPBUSM
    elif product in UPBKindUSM2:
        return UPBUSM
    elif product in UPBKindTEC:
        return UPBTEC
    elif product in UPBKindESI:
        return UPBESI
    elif product in UPBKindAPI:
        return UPBAPI
    elif product in UPBKindRFI:
        return UPBRFI
    else:
        return None

