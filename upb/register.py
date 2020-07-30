from struct import unpack
from enum import Enum
from ctypes import Structure, BigEndianStructure, c_uint8, c_uint16, c_uint32, c_ubyte, c_char, Array
from collections import defaultdict

from upb.memory import *

class Dictionary:
    # Implement the iterator method such that dict(...) results in the correct
    # dictionary.
    def __iter__(self):
        subtypes = (RockerAction, UPBButtonAction, UPBIndicator, UPBInput, IOMInput, TimedEvent, ESIComponent)
        for k, t in self._fields_:
            if k not in {'reserved1', 'reserved2', 'reserved3', 'reserved4', 'reserved5'}:
                if isinstance(t, subtypes):
                    nd = defaultdict(dict)
                    for nk, nt in t._fields_:
                        nd[nk] = getattr(t, nk)
                    yield (k, dict(nd))
                elif (issubclass(t, Structure)):
                    for nk, nt in getattr(self, k):
                        yield (nk, getattr(self, nk))
                elif (issubclass(t, Array)):
                    ak = getattr(self, k)
                    al = []
                    for ai in range(len(ak)):
                        av = ak[ai]
                        if isinstance(av, subtypes):
                            nd = defaultdict(dict)
                            for nk, nt in av._fields_:
                                nd[nk] = getattr(av, nk)
                            al.append(dict(nd))
                        else:
                            al.append(av)
                    yield (k, al)
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

class UPBSwitch(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_ids', c_uint8 * 16),
                ('preset_level_table', c_uint8 * 16),
                ('preset_fade_table', c_uint8 * 16),
                ('top_rocker_tid', c_uint8),
                ('top_rocker_single_click', c_uint8),
                ('top_rocker_double_click', c_uint8),
                ('top_rocker_hold', c_uint8),
                ('top_rocker_release', c_uint8),
                ('bottom_rocker_tid', c_uint8),
                ('bottom_rocker_single_click', c_uint8),
                ('bottom_rocker_double_click', c_uint8),
                ('bottom_rocker_hold', c_uint8),
                ('bottom_rocker_release', c_uint8),
                ('top_rocker_sc_level', c_uint8),
                ('top_rocker_sc_rate', c_uint8),
                ('top_rocker_dc_level', c_uint8),
                ('top_rocker_dc_rate', c_uint8),
                ('bottom_rocker_sc_level', c_uint8),
                ('bottom_rocker_sc_rate', c_uint8),
                ('bottom_rocker_dc_level', c_uint8),
                ('bottom_rocker_dc_rate', c_uint8),
                ('reserved1', c_char * 6),
                ('min_dim_level', c_uint8),
                ('auto_off_link', c_uint8),
                ('auto_off_cmd', c_uint8),
                ('led_options', c_uint8),
                ('switch_options', c_uint8),
                ('default_options', c_uint8),
                ('transmission_options', c_uint8),
                ('timed_options', c_uint8),
                ('reserved2', c_char * 112)]

class UPBModule(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_ids', c_uint8 * 16),
                ('preset_level_table', c_uint8 * 16),
                ('preset_fade_table', c_uint8 * 16),
                ('reserved1', c_char * 23),
                ('lts_link', c_uint8),
                ('lts_cmd', c_uint8),
                ('auto_off_link', c_uint8),
                ('auto_off_cmd', c_uint8),
                ('led_options', c_uint8),
                ('options', c_uint8),
                ('default_options', c_uint8),
                ('transmission_options', c_uint8),
                ('timed_options', c_uint8),
                ('reserved3', c_char * 112)]

class UPBModule2(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_ids_1', c_uint8 * 16),
                ('preset_level_table_1', c_uint8 * 16),
                ('preset_fade_table_1', c_uint8 * 16),
                ('link_ids_2', c_uint8 * 16),
                ('preset_level_table_2', c_uint8 * 16),
                ('preset_fade_table_2', c_uint8 * 16),
                ('default_options', c_uint8),
                ('transmission_options', c_uint8),
                ('led_options', c_uint8),
                ('options', c_uint8),
                ('transmit_link', c_uint8),
                ('transmit_cmd', c_uint8),
                ('transmit_link_2', c_uint8),
                ('transmit_cmd_2', c_uint8),
                ('reserved2', c_char * 24),
                ('timed_options_1', c_uint8),
                ('timed_options_2', c_uint8),
                ('timed_options_3', c_uint8),
                ('timed_options_4', c_uint8),
                ('auto_off_link_1', c_uint8),
                ('auto_off_cmd_1', c_uint8),
                ('auto_off_link_2', c_uint8),
                ('auto_off_cmd_2', c_uint8),
                ('reserved4', c_char * 56)]

class UPBButtonAction(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('link', c_uint8),
                ('single_click', c_uint8),
                ('double_click', c_uint8),
                ('hold', c_uint8),
                ('release', c_uint8)]

class UPBIndicator(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('link', c_uint8),
                ('preset1', c_uint8),
                ('preset2', c_uint8)]

class UPBKeypad(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('indicator_links', c_uint8 * 8),
                ('button_action_table', UPBButtonAction * 8),
                ('led_group_table', c_uint8 * 8),
                ('reserved1', c_char * 18),
                ('use_options', c_uint8),
                ('reserved2', c_char),
                ('ir_options', c_uint8),
                ('led_options', c_uint8),
                ('transmission_options', c_uint8),
                ('indicator_options', c_uint8),
                ('reserved3', c_char * 48),
                ('indicator_table', UPBIndicator * 16),
                ('reserved4', c_char * 16)]

class UPBKeypadDimmer(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_ids', c_uint8 * 16),
                ('preset_level_table', c_uint8 * 16),
                ('preset_fade_table', c_uint8 * 16),
                ('indicator_table', UPBIndicator * 16),
                ('button_action_table', UPBButtonAction * 8),
                ('reserved1', c_char * 42),
                ('min_dim_level', c_uint8),
                ('use_options', c_uint8),
                ('reserved2', c_char),
                ('led_options', c_uint8),
                ('dim_options', c_uint8),
                ('chirp_options', c_uint8),
                ('transmission_options', c_uint8),
                ('transmission_enable', c_uint8),
                ('auto_off_time', c_uint8),
                ('auto_off_link', c_uint8),
                ('auto_off_cmd', c_uint8),
                ('reserved3', c_char * 3)]

class UPBInput(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('open_link_id', c_uint8),
                ('open_cmd_id', c_uint8),
                ('close_link_id', c_uint8),
                ('close_cmd_id', c_uint8)]

class UPBICM(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
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
                ('transmit_timeout', c_uint8),
                ('transmit_attempts', c_uint8),
                ('led_options', c_uint8),
                ('input_debounce_count', c_uint8),
                ('reserved3', c_char),
                ('transmission_options', c_uint8),
                ('heartbeat_period', c_uint8),
                ('reserved4', c_char * 112)]

class RockerAction(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('top_rocker_tid', c_uint8),
                ('top_rocker_single_click', c_uint8),
                ('top_rocker_double_click', c_uint8),
                ('top_rocker_hold', c_uint8),
                ('top_rocker_release', c_uint8),
                ('bottom_rocker_tid', c_uint8),
                ('bottom_rocker_single_click', c_uint8),
                ('bottom_rocker_double_click', c_uint8),
                ('bottom_rocker_hold', c_uint8),
                ('bottom_rocker_release', c_uint8)]

class UPBUSQ(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_ids', c_uint8 * 16),
                ('preset_level_table', c_uint8 * 16),
                ('preset_fade_table', c_uint8 * 16),
                ('rocker1', RockerAction),
                ('top_rocker_sc_level', c_uint8),
                ('top_rocker_sc_rate', c_uint8),
                ('top_rocker_dc_level', c_uint8),
                ('top_rocker_dc_rate', c_uint8),
                ('bottom_rocker_sc_level', c_uint8),
                ('bottom_rocker_sc_rate', c_uint8),
                ('bottom_rocker_dc_level', c_uint8),
                ('bottom_rocker_dc_rate', c_uint8),
                ('reserved2', c_char * 8),
                ('tap_options', c_uint8),
                ('led_options', c_uint8),
                ('rocker_config', c_uint8),
                ('default_options', c_uint8),
                ('transmission_options', c_uint8),
                ('rocker_options', c_uint8),
                ('reserved3', c_char * 58),
                ('rocker_2_to_4', RockerAction * 3),
                ('reserved4', c_char * 24)]

class UPBUS4(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('reserved1', c_char * 32),
                ('rockers', RockerAction * 4),
                ('dim_options_1', c_uint8),
                ('dim_options_2', c_uint8),
                ('dim_options_3', c_uint8),
                ('dim_options_4', c_uint8),
                ('led_options', c_uint8),
                ('button_config', c_uint8),
                ('transmission_options', c_uint8),
                ('variant_options', c_uint8),
                ('misc_options', c_uint8),
                ('button_transmit_options', c_uint8),
                ('output_options', c_uint8),
                ('reserved2', c_char * 3),
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
                ('reserved3', c_char * 10)]

class UPBUS22(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('reserved1', c_char * 32),
                ('rockers', RockerAction * 4),
                ('dim_options_1', c_uint8),
                ('dim_options_2', c_uint8),
                ('reserved2', c_char * 2),
                ('led_options', c_uint8),
                ('button_config', c_uint8),
                ('transmission_options', c_uint8),
                ('variant_options', c_uint8),
                ('misc_options', c_uint8),
                ('button_transmit_options', c_uint8),
                ('output_options', c_uint8),
                ('reserved3', c_char * 3),
                ('link_ids_1', c_uint8 * 16),
                ('preset_level_table_1', c_uint8 * 16),
                ('preset_fade_table_1', c_uint8 * 16),
                ('link_ids_2', c_uint8 * 16),
                ('preset_level_table_2', c_uint8 * 16),
                ('preset_fade_table_2', c_uint8 * 16),
                ('reserved4', c_char * 10)]

class UPBUS2(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_ids', c_uint8 * 16),
                ('preset_level_table', c_uint8 * 16),
                ('preset_fade_table', c_uint8 * 16),
                ('reserved1', c_char * 26),
                ('rocker_transmit_options', c_uint8),
                ('led_options', c_uint8),
                ('rocker_config', c_uint8),
                ('dim_options', c_uint8),
                ('transmission_options', c_uint8),
                ('rocker_options', c_uint8),
                ('rocker_action', RockerAction * 4),
                ('reserved2', c_char * 72)]

class UPBUFQ(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('button_action_table', UPBButtonAction * 4),
                ('reserved1', c_char * 55),
                ('led_options', c_uint8),
                ('reserved2', c_char * 2),
                ('transmission_options', c_uint8),
                ('reserved3', c_char),
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
                ('timeout_enables', c_uint8),
                ('timeout_1', c_uint8),
                ('timeout_2', c_uint8),
                ('timeout_3', c_uint8),
                ('timeout_4', c_uint8),
                ('variant_options', c_uint8),
                ('reserved5', c_char * 8)]

class IOMInput(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('close_link_id', c_uint8),
                ('close_cmd', c_uint8),
                ('close_b1', c_uint8),
                ('close_b2', c_uint8),
                ('open_link_id', c_uint8),
                ('open_cmd', c_uint8),
                ('open_b1', c_uint8),
                ('open_b2', c_uint8)]

class UPBIOM(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_ids_1', c_uint8 * 16),
                ('state_1', c_uint8 * 16),
                ('unused_1', c_uint8 * 16),
                ('link_ids_2', c_uint8 * 16),
                ('state_2', c_uint8 * 16),
                ('unused_2', c_uint8 * 16),
                ('input', IOMInput * 3),
                ('reserved1', c_char * 8),
                ('transmission_options', c_uint8),
                ('led_options', c_uint8),
                ('reserved2', c_char),
                ('device_options', c_uint8),
                ('reserved3', c_char * 60)]

class UPBFR(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_ids', c_uint8 * 16),
                ('preset_level_table', c_uint8 * 16),
                ('preset_fade_table', c_uint8 * 16),
                ('rocker', RockerAction),
                ('top_rocker_sc_level', c_uint8),
                ('top_rocker_sc_rate', c_uint8),
                ('top_rocker_dc_level', c_uint8),
                ('top_rocker_dc_rate', c_uint8),
                ('bottom_rocker_sc_level', c_uint8),
                ('bottom_rocker_sc_rate', c_uint8),
                ('bottom_rocker_dc_level', c_uint8),
                ('bottom_rocker_dc_rate', c_uint8),
                ('reserved1', c_char * 8),
                ('tap_options', c_uint8),
                ('led_options', c_uint8),
                ('reserved2', c_char),
                ('output_options', c_uint8),
                ('transmission_options', c_uint8),
                ('rocker_options', c_uint8),
                ('reserved3', c_char * 112)]

class UPBUSM(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('rocker1', RockerAction),
                ('rocker2', RockerAction),
                ('reserved1', c_char * 46),
                ('calib_0', c_uint8),
                ('calib_1', c_uint8),
                ('calib_2', c_uint8),
                ('calib_3', c_uint8),
                ('reserved2', c_char * 4),
                ('rocker_transmit', c_uint8),
                ('led_options', c_uint8),
                ('byte_1', c_uint8),
                ('byte_2', c_uint8),
                ('byte_3', c_uint8),
                ('calib_scale', c_uint8),
                ('link_ids_1', c_uint8 * 8),
                ('preset_level_table_1', c_uint8 * 8),
                ('preset_fade_table_1', c_uint8 * 8),
                ('link_ids_2', c_uint8 * 8),
                ('preset_level_table_2', c_uint8 * 8),
                ('preset_fade_table_2', c_uint8 * 8),
                ('reserved4', c_char * 64)]

class DSTDate(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('start_month', c_uint8),
                ('start_day', c_uint8),
                ('end_month', c_uint8),
                ('end_day', c_uint8)]

class TECFlash(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('clock', c_uint8 * 8),
                ('jan_1_sunrise_hours', c_uint8),
                ('jan_1_sunrise_minutes', c_uint8),
                ('jan_1_sunset_hours', c_uint8),
                ('jan_1_sunset_minutes', c_uint8),
                ('dst_start_month', c_uint8),
                ('dst_start_day', c_uint8),
                ('dst_stop_month', c_uint8),
                ('dst_stop_day', c_uint8),
                ('suntime_table', c_uint8 * 366),
                ('dst_table', DSTDate * 30)]

class TimedEvent(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('time1', c_uint8),
                ('time2', c_uint8),
                ('minute', c_uint8),
                ('vary', c_uint8),
                ('transmit_link', c_uint8),
                ('transmit_cmd', c_uint8),
                ('receive_link', c_uint8),
                ('receive_level', c_uint8)]

class UPBTEC(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('led_options', c_uint8),
                ('transmission_options', c_uint8),
                ('reserved1', c_char * 5),
                ('ct_events_in_use', c_uint8),
                ('event_table', TimedEvent * 20),
                ('reserved2', c_char * 24)]

class ESIComponent(BigEndianStructure):
    _pack_ = 1
    _fields_ = [('link_id', c_uint8),
                ('cm_msg', c_uint8),
                ('msg', c_uint8 * 7)]

class UPBESI(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('rct', ESIComponent * 16),
                ('reserved1', c_char * 16),
                ('transmission_options', c_uint8),
                ('led_options', c_uint8),
                ('reserved2', c_char * 30)]

class UPBAPI(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('house_code_map', c_uint8 * 16),
                ('command_map', c_uint8 * 16),
                ('reserved1', c_char * 46),
                ('transmission_options', c_uint8),
                ('reserved2', c_char * 113)]

class UPBRFI(BigEndianStructure, Dictionary):
    _pack_ = 1
    _anonymous_ = ('upbid',)
    _fields_ = [('upbid', UPBID),
                ('link_id', c_uint8 * 32),
                ('scdc', c_uint8 * 32),
                ('hold_release', c_uint8 * 32),
                ('remote_type', c_uint8 * 32),
                ('name_update', c_uint8),
                ('reserved1', c_char * 2),
                ('led_options', c_uint8),
                ('reserved2', c_char * 2),
                ('transmission_options', c_uint8),
                ('reserved3', c_char * 49),
                ('remote_1_id', c_uint8 * 4),
                ('remote_2_id', c_uint8 * 4),
                ('remote_3_id', c_uint8 * 4),
                ('remote_4_id', c_uint8 * 4),
                ('remote_5_id', c_uint8 * 4),
                ('remote_6_id', c_uint8 * 4),
                ('remote_7_id', c_uint8 * 4),
                ('remote_8_id', c_uint8 * 4)]

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

