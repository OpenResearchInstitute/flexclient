import itertools


class Slice(object):
	""" A Class to create, remove and alter radio frequency slices """
	Id_iter = itertools.count() # slice_id needs to be a unique attribute for each slice 

	def __init__(self, radio, freq, ant, mode):
		self.slice_id = next(self.Id_iter)
		self.radio = radio
		self.rxant = ant
		if freq < 0.03:
			self.RF_frequency = 0.03
			# log attempt to set below min
		elif freq > 54.0:
			self.RF_frequency = 54.0
			# log attempt to set above max
		else:
			self.RF_frequency = freq

		self.mode = mode.upper()


	def Remove(self):
		command = "slice r " + str(self.slice_id)
		self.radio.SendCommand(command)


	def Tune(self, freq):
		if freq < 0.03:
			self.RF_frequency = 0.03
			# log attempt to set below min
		elif freq > 54.0:
			self.RF_frequency = 54.0
			# log attempt to set above max
		else:
			self.RF_frequency = freq

		command = "slice t " + str(self.slice_id) + " " + str(self.RF_frequency)
		self.radio.SendCommand(command)


	def Set(self, **kwargs):
		command = "slice s " + str(self.slice_id)
		for param, arg in kwargs.items():
			command += (" " + param + "=" + str(arg))

		self.radio.SendCommand(command)

