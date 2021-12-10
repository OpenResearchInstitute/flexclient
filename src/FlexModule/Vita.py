

class VitaPacket(object):
	""" class to parse a vita packet """

	def __init__(self, data):
		self.pkt_type = data[0] & int('F0',16) >> 4
		self.pkt_count = data[1] & int('F',16)
		# self.pkt_type = int.from_bytes(data[0:2], byteorder='big')
		self.pkt_size = int.from_bytes(data[2:4], byteorder='big') * 4
		self.stream_id = data[4:8]
		self.class_id = data[8:16]
		self.date_stamps = data[16:28]	# not implemented by FLEX
		self.payload = data[28:self.pkt_size+1]

		if self.pkt_size != len(data):
			print("Packet length error")


