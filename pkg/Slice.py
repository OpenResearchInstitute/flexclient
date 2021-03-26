import itertools


class Slice(object):
	""" A Class to create, remove and alter radio frequency slices """
	Id_iter = itertools.count() # slice_id needs to be a unique attribute for each slice 

	def __init__(self, radio, freq, ant, mode, streamID=None, source_slice=None):
		self.slice_id = next(self.Id_iter)
		self.radio = radio

		if freq < 0.03:
			self.freq = 0.03
			# log attempt to set below min
		elif freq > 54:
			self.freq = 54
			# log attempt to set above max
		else:
			self.freq = freq

		self.ant = ant
		
		self.mode = mode

		command = "slice create"
		command += (" freq=" + str(self.freq))
		if streamID is not None:
			self.streamID = streamID
			command += (" pan=0x" + str(self.streamID))
		command += (" ant=" + self.ant)
		command += (" mode=" + self.mode)
		if source_slice is not None:
			command += (" clone_slice=" + str(source_slice))
		
		self.radio.SendCommand(command)
		# add reply expected to reply list = R21|0|0


	def Remove(self):
		command = "slice r " + str(self.slice_id)
		self.radio.SendCommand(command)
		# add reply expected to reply list R|19|0|


	def Tune(self, freq):
		if freq < 0.03:
			self.freq = 0.03
			# log attempt to set below min
		elif freq > 54:
			self.freq = 54
			# log attempt to set above max
		else:
			self.freq = freq

		command = "slice t " + str(self.slice_id) + " " + str(self.freq)
		self.radio.SendCommand(command)
		#add reply expected to reply list = R12|0||


	def Set(self, **kwargs):
		command = "slice s " + str(self.slice_id)
		for param, arg in kwargs.items():
			command += (" " + param + "=" + str(arg))

		self.radio.SendCommand(command)
		#add reply expected to reply list = R41|0|...


