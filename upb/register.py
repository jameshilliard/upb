from struct import unpack

def reg_decode(reg):
	upbid = {
		'net_id': reg[0],
		'module_id': reg[1],
		'password': unpack('>H', reg[2:4])[0],
		'upb_options': reg[4],
		'upb_version': reg[5],
		'manufacturer_id': unpack('>H', reg[6:8])[0],
		'product_id': unpack('>H', reg[8:10])[0],
		'firmware_major_version': reg[10],
		'firmware_minor_version': reg[11],
		'serial_number': unpack('>I', reg[12:16])[0]
	}
	return upbid
