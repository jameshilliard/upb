from functools import reduce


def cksum(data):
	return (256 - reduce(lambda x, y: x + y, data)) % 256

