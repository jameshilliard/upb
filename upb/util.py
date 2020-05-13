from struct import pack
from functools import reduce

from upb.const import UpbDeviceId, UpbReqRepeater, UpbReqAck, MdidSet, MdidCoreCmd, PimCommand


def cksum(data):
	return (256 - reduce(lambda x, y: x + y, data)) % 256

def encode_register_request(network, device, register_start=0, registers=16):
    """Encode a message for the PIM"""
    cnt = 0
    seq = 0
    link = False
    data_len = 9
    network_id = network
    destination_id = device
    device_id = UpbDeviceId.DEFAULT_DEVICEID.value
    link_bit = (1 if link else 0) << 7
    repeater_request = UpbReqRepeater.REP_NONREPEATER.value << 5
    ack_request = UpbReqAck.REQ_ACKNOREQUEUEONNAK.value << 4
    transmit_cnt = cnt << 2
    transmit_seq = seq
    control_word = pack('BB', *[data_len | link_bit | repeater_request, ack_request | transmit_cnt | transmit_seq])
    mdid_set = MdidSet.MDID_CORE_COMMANDS.value
    mdid_cmd = MdidCoreCmd.MDID_CORE_COMMAND_GETREGISTERVALUES.value
    print(f"control: {control_word}, len: {len(control_word)}")
    msg = control_word
    msg += pack('B', network_id)
    msg += pack('B', destination_id)
    msg += pack('B', device_id)
    msg += pack('B', mdid_set | mdid_cmd)
    msg += pack('B', register_start)
    msg += pack('B', registers)
    msg += pack('B', cksum(msg))
    packet = pack('B', PimCommand.UPB_NETWORK_TRANSMIT.value)
    packet += msg.hex().upper().encode('ascii')
    return packet