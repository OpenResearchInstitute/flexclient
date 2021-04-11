import itertools


class Slice(object):
	""" A Class to create, remove and alter radio frequency slices """
	Id_iter = itertools.count() # slice_id needs to be a unique attribute for each slice 

	def __init__(self, radio, freq, ant, mode):
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
		
		self.mode = mode.upper()


	def Remove(self):
		command = "slice r " + str(self.slice_id)
		self.radio.SendCommand(command)


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


	def Set(self, **kwargs):
		command = "slice s " + str(self.slice_id)
		for param, arg in kwargs.items():
			command += (" " + param + "=" + str(arg))

		self.radio.SendCommand(command)

