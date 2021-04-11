from queue import Queue

class RxRemoteAudioStream(object):
	"""class for a RX Remote Audio Stream """

	def __init__(self, radio, stream_id, isCompressed):
		# super(RXRemoteAudioStream, self).__init__()
		self.radio = radio
		self.stream_id = stream_id
		self.isCompressed = isCompressed
		self.outBuffer = Queue()
		# self.RxGain = 50


	def Close(self):
		command = "stream remove 0x" + self.stream_id
		self.radio.SendCommand(command)


	# def SetRxGain(self, rg):
	# 	if rg > 100:
	# 		rg = 100
	# 	elif rg < 0:
	# 		rg = 0
	
	def WriteToFile(self):
		with open("sample.bin", "wb") as outfile:
			for i in range(self.outBuffer.qsize()):
				outfile.write(self.outBuffer.get())