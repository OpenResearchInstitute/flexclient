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
		self.fps = 0

		self.PanBuffer = Queue()
		self.WatBuffer = Queue()
		# self.RxGain = 50


	def Set(self, **kwargs):
		command = "display panf s " + str(self.panadapter_id)
		for param, arg in kwargs.items():
			command += (" " + param + "=" + str(arg))

		self.radio.SendCommand(command)


"""
display pan set 0x40000000 x=100 y=20

The radio will send an array of values between 0-20.  These values are Y.  The position of value (Bin) is X.  So lets take these values from a single packet and place them in an array.  
You should end up with an Array that has a length of 100 and contains values between 0-20.  The lower the the value the higher the signal strength. 

The index of the array is the X value, and the value at that index is Y.  Now you jut need to plot those values on the screen. You will plot from 0,0 which is the upper left corner of the window. 

Now you just need to create a for loop to draw lines

drawline from index,array[index] to index+1,array[index+1]
increment index and repeat till index = array length-1 (99 in this example)

Clear window
read next packet and do it again.
"""



