from queue import Queue

class Panafall(object):
	"""class for a Panafall display object """

	def __init__(self, radio, p_id, w_id, freq, x, y):
		# super(RXRemoteAudioStream, self).__init__()
		self.radio = radio
		self.panadapter_id = p_id
		self.waterfall_id = w_id
		self.center = freq
		self.x_pixels = x
		self.y_pixels = y

		# useful parameters that are unknown on intialisation
		self.rxant = ""
		self.daxiq_channel = 0
		self.band = 0
		self.bandwidth = 0.0
		self.min_dbm = 0
		self.max_dbm = 0
		self.fps = 0
		self.rfgain = 0

		self.PanBuffer = Queue()
		self.WatBuffer = Queue()


	def Set(self, **kwargs):
		command = "display panf s " + str(self.panadapter_id)
		for param, arg in kwargs.items():
			command += (" " + param + "=" + str(arg))

		self.radio.SendCommand(command)




