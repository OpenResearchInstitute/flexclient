"""
Need to find a way to reference radio outside the Main() context
Also myRadio needs to have attributes and methods, but shouldn't be defined in Initialiser.py
"""

class Slice(object):

	def __init__(self, freq, ant, mode, streamID=None, source_slice=None):
		if freq < 0.03:
			self.freq = 0.03
			# log attempt to set below min
		elif freq > 54:
			self.freq = 54
			# log attempt to set above max
		else:
			self.freq = freq

		ant_list = myRadio.GetAnts() #GetAnts(Rx/Tx)?
		if ant in ant_list:
			self.ant = ant
		else:
			raise Exception("Chosen Antenna not available")
		
		self.mode = mode

		command = "C21|slice create"
		command += (" freq=" + str(self.freq))
		if streamID is not None:
			self.streamID = streamID
			command += (" pan=0x" + str(self.streamID))
		command += (" ant=" + ant)
		command += (" mode=" + mode)
		if source_slice is not None:
			command += (" clone_slice=" + str(source_slice))
		
		myRadio.SendCommand(command)
		# myRadio.AddSlice(self)
		# add reply expected to reply list = R21|0|0


	def Remove(self, slice_rx):
		command = "C19|slice r " + str(slice_rx)
		myRadio.SendCommand(command)
		# myRadio.RemoveSlice(self)


	def Tune(self, slice_rx, freq):
		if freq < 0.03:
			self.freq = 0.03
			# log attempt to set below min
		elif freq > 54:
			self.freq = 54
			# log attempt to set above max
		else:
			self.freq = freq

		command = "C12|slice t " + str(slice_rx) + str(self.freq)
		myRadio.SendCommand(command)
		#add reply expected to reply list = R12|0||


	def Set(self, slice_rx, **kwargs):
		command = "C41|slice s " + str(slice_rx)
		for param, arg in self.kwargs.items():
			command += (" " + param + "=" + str(arg))

		myRadio.SendCommand(command)
		#add reply expected to reply list = R41|0|...


