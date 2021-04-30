from numpy import array
from queue import Queue
from scipy.io.wavfile import write

class RxRemoteAudioStream(object):
	"""class for a RX Remote Audio Stream """

	def __init__(self, radio, stream_id, isCompressed):
		# super(RXRemoteAudioStream, self).__init__()
		self.radio = radio
		self.stream_id = stream_id
		self.isCompressed = isCompressed
		self.outBuffer = Queue()
		# self.outBuffer = []
		# self.RxGain = 50


	# def Close(self):
	# 	command = "stream remove 0x" + self.stream_id
	# 	self.radio.SendCommand(command)


	# def SetRxGain(self, rg):
	# 	if rg > 100:
	# 		rg = 100
	# 	elif rg < 0:
	# 		rg = 0
	
	def WriteToFile(self):
		temp = []
		samplerate = 44100
		for i in range(self.outBuffer.qsize()):
			temp.append(self.outBuffer.get())

		wavArr = array(temp, dtype=float)

		write("example.wav", samplerate, wavArr)