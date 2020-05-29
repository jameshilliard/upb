from struct import pack
from functools import reduce
from binascii import hexlify

from upb.const import UpbDeviceId, UpbReqRepeater, UpbReqAck, MdidSet, MdidCoreCmd, PimCommand


def cksum(data):
    return (256 - reduce(lambda x, y: x + y, data)) % 256

def format_transmit_packet(network, device, cmd, data=None, link=False, ack=UpbReqAck.REQ_ACKNOREQUEUEONNAK,
    repeat=UpbReqRepeater.REP_NONREPEATER, cnt=0, seq=0):
    """Encode a transmit message for the PIM"""
    data_len = 7
    if data is not None:
        data_len += len(data)
    network_id = network
    destination_id = device
    device_id = UpbDeviceId.DEFAULT_DEVICEID.value
    link_bit = (1 if link else 0) << 7
    repeater_request = repeat.value << 5
    ack_request = ack.value << 4
    transmit_cnt = cnt << 2
    transmit_seq = seq
    control_word = pack('BB', *[data_len | link_bit | repeater_request, ack_request | transmit_cnt | transmit_seq])
    if isinstance(cmd, MdidCoreCmd):
        mdid_set = MdidSet.MDID_CORE_COMMANDS.value
    mdid_cmd = cmd.value
    msg = control_word
    msg += pack('B', network_id)
    msg += pack('B', destination_id)
    msg += pack('B', device_id)
    msg += pack('B', mdid_set | mdid_cmd)
    if data is not None:
        msg += data
    msg += pack('B', cksum(msg))
    return msg

def encode_register_request(network, device, register_start=0, registers=16):
    """Encode a register request for the PIM to transmit"""
    mdid_cmd = MdidCoreCmd.MDID_CORE_COMMAND_GETREGISTERVALUES
    data = pack('B', register_start) + pack('B', registers)
    packet = format_transmit_packet(network, device, mdid_cmd, data)
    return packet

def encode_signature_request(network, device):
    """Encode a message for the PIM"""
    mdid_cmd = MdidCoreCmd.MDID_CORE_COMMAND_GETDEVICESIGNATURE
    packet = format_transmit_packet(network, device, mdid_cmd)
    return packet

def encode_startsetup_request(network, device, password):
    """Encode a message for the PIM"""
    mdid_cmd = MdidCoreCmd.MDID_CORE_COMMAND_STARTSETUP
    data = pack('>H', password)
    packet = format_transmit_packet(network, device, mdid_cmd, data)
    return packet

def encode_setuptime_request(network, device):
    """Encode a message for the PIM"""
    mdid_cmd = MdidCoreCmd.MDID_CORE_COMMAND_GETSETUPTIME
    packet = format_transmit_packet(network, device, mdid_cmd)
    return packet

def hexdump(data, length=None, sep=':'):
    if length is not None:
        lines = ""
        for seq in range(0, len(data), 16):
            line = data[seq: seq + 16]
            lines += sep.join("{:02x}".format(c) for c in line) + "\n"
    else:
        lines = sep.join("{:02x}".format(c) for c in data)
    return lines
