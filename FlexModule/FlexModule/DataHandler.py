import http.client, pdb, socket, ssl, threading, select
from .Vita import VitaPacket
from .RxRemoteAudioStream import RxRemoteAudioStream
from .Panafall import Panafall
from struct import *

class ReceiveData(threading.Thread):
	""" Thread to contiually receive tcp data in BG """
	def __init__(self, radio):
		threading.Thread.__init__(self, daemon=True)
		self.radio = radio
		self.running = True
		# self.read_socks = []

	def run(self):
		read_socks = [self.radio.FLEX_Sock, self.radio.DATA_Sock]
		tcpResponse = ""
		udpResponse = ""
		while read_socks:
			readable, w, e = select.select(read_socks,[],[],0)
			for s in readable:
				if s.type == 1: # "SOCK_STREAM"
					data = s.recv(512).decode("cp1252")
					tcpResponse += data
					if data.endswith("\n"):
						ParseRead(self.radio, tcpResponse.rstrip())
						tcpResponse = ""
				elif s.type == 2: # "SOCK_DGRAM"
					udpResponse, addr = s.recvfrom(8192)
					# print(udpResponse)
					ParseVitaPacket(self.radio, VitaPacket(udpResponse))

				# if not data:
				# 	read_socks.remove(s)
			if not self.running:
				read_socks.clear()



def ParseRead(radio, string):
	# print(string)
	read_type = string[0]
	if read_type == "R":
		print(string)
		ParseReply(radio, string)
	elif read_type == "S":
		ParseStatus(radio, string)
	elif read_type == "M":
		ParseMessage(radio, string)
	elif read_type == "H":
		ParseHandle(radio, string)
	elif read_type == "V":
		ParseVersion(radio, string)
	else:
		print("Unknown response from radio: " + radio.radioData["serial"]) 


def ParseReply(radio, string):
	try:
		(response_code, hex_code, rec_msg) = string.split('|')
	except ValueError:
		print("Error - Incomplete reply")
		return

	response_code = int(response_code[1:])
	hex_code = int(hex_code, 16)
	# rec_msg = rec_msg.strip()
	try:
		sent_msg = radio.ResponseList[response_code]
	except ValueError:
		print('Unexpected reply')
	
	if "slice c" in sent_msg:
		if hex_code != 0:
			# log error
			# remove slice from slice list
			pass
		
	elif "slice r" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		else:
			# remove self now that radio has confirmed deletion
			s_id = int(sent_msg[-1])
			radio.SliceList.remove(radio.GetSlice(s_id))
	elif "slice list" in sent_msg:
		if hex_code != 0:
			# log error
			pass
	elif "ant list" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		radio.AntList = rec_msg.split(sep=",")
	elif "stream c" in sent_msg:
		if hex_code != 0:
			# log error
			radio.RxAudioStreamer = None	# unsuccessful creation on radio side
			pass
		else:
			if "type=remote_audio_rx" in sent_msg:
				streamCompression = sent_msg.split("compression=")[1]
				if streamCompression == "opus":
					radio.RxAudioStreamer = RxRemoteAudioStream(radio, rec_msg, True)
				else:
					radio.RxAudioStreamer = RxRemoteAudioStream(radio, rec_msg, False)
	elif "stream r" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		else:
			# s_id = sent_msg.split("remove 0x")[1]
			radio.RxAudioStreamer = None
	elif "display panafall c" in sent_msg:
		if hex_code != 0:
			# log error
			radio.Panafall = None	# unsuccessful creation on radio side
			pass
		else:
			p_id, w_id = rec_msg.split(',')
			pan_data = dict(param.split("=") for param in sent_msg.split(" ")[3:])

			radio.Panafall = Panafall(radio, p_id, w_id, float(pan_data["freq"]), int(pan_data["x"]), int(pan_data["y"]))
	elif "display panf s" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		else:
			# For some reason, the radio expects a different term to one it returns for these two ¯\_(ツ)_/¯
			# if key is "xpixels":
			# 	setattr(radio.Panafall, "x_pixels", float(value))
			# elif key is "ypixels":
			# 	setattr(radio.Panafall, "y_pixels", float(value))
			pass
	elif "display panf r" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		else:
			radio.Panafall = None

	radio.ResponseList.pop(response_code)


def ParseStatus(radio, string):
	try:
		(radio_handle, rec_msg) = string.split('|')
	except ValueError:
		print("Error - Invalid status message")
		return

	if radio_handle == "S" + radio.clientHandle:  # status message for this client i.e you
		if rec_msg.startswith("slice"):
			# print(rec_msg)
			if "removed" in rec_msg:
				return
			split_msg = rec_msg.split(sep=' ', maxsplit=2)
			s_id = int(split_msg[1])
			slice_info = dict(param.split("=") for param in split_msg[2].split(" "))
			
			""" handler errors here if radio creates slice without us knowing about it e.g. when Panadapter is created """
			try:
				radio.GetSlice(s_id)
			except IndexError:
				return

			for key, value in slice_info.items():
				# check to see if class attribute exists
				try:
					val_type = type(getattr(radio.GetSlice(s_id), key))
				except AttributeError:
					# I haven't implemented this variable, i didn't require it at this point and wanted to keep class uncluttered
					continue

				# if class attribute is numerical, we want to keep it numerical
				if val_type is float or val_type is int:
					setattr(radio.GetSlice(s_id), key, float(value))
				else:
					setattr(radio.GetSlice(s_id), key, value)
			
			""" 
			slice 0 in_use=1 RF_frequency=14.100000 client_handle=0x6D616CE3 index_letter=A rit_on=0 rit_freq=0 xit_on=0 xit_freq=0 rxant=ANT1 
			mode=USB wide=0 filter_lo=100 filter_hi=2800 step=100 step_list=1,10,50,100,500,1000,2000,3000 agc_mode=med agc_threshold=65 
			agc_off_level=10 pan=0x40000000 txant=ANT1 loopa=0 loopb=0 qsk=0 dax=1 dax_clients=0 lock=0 tx=1 active=1 audio_level=50 audio_pan=50 
			audio_mute=0 record=0 play=disabled record_time=0.0 anf=0 anf_level=50 nr=0 nr_level=50 nb=0 nb_level=50 wnb=0 wnb_level=0 apf=0 
			apf_level=0 squelch=1 squelch_level=20 diversity=0 diversity_parent=0 diversity_child=0 diversity_index=1342177293 
			ant_list=ANT1,ANT2,RX_A,XVTA mode_list=LSB,USB,AM,CW,DIGL,DIGU,SAM,FM,NFM,DFM,RTTY fm_tone_mode=OFF fm_tone_value=67.0 
			fm_repeater_offset_freq=0.000000 tx_offset_freq=0.000000 repeater_offset_dir=SIMPLEX fm_tone_burst=0 fm_deviation=5000 
			dfm_pre_de_emphasis=0 post_demod_low=300 post_demod_high=3300 rtty_mark=2125 rtty_shift=170 digl_offset=2210 digu_offset=1500 
			post_demod_bypass=0 rfgain=0 tx_ant_list=ANT1,ANT2,XVTA
			"""
		elif rec_msg.startswith("radio"):
			pass
		elif rec_msg.startswith("display pan"):
			# print(rec_msg)
			if "removed" in rec_msg:
				return
			split_msg = rec_msg.split(sep=' ', maxsplit=3)
			p_id = split_msg[2]
			pan_info = dict(param.split("=") for param in split_msg[3].split(" "))

			if not radio.Panafall or radio.Panafall.panadapter_id != p_id:
				# no point trying to update radio's panafall if it doesn't exist
				return 

			for key, value in pan_info.items():
				# for key, value pair in subscription string, try to update the Panafall object if the key has been defined. 

				try:
					val_type = type(getattr(radio.Panafall, key))
				except AttributeError:
					continue

				if val_type is float or val_type is int:
					setattr(radio.Panafall, key, float(value))
				else:
					setattr(radio.Panafall, key, value)
			"""
			display pan 0x40000000 client_handle=0xE8360D29 wnb=0 wnb_level=0 wnb_updating=1 band_zoom=0 segment_zoom=0 x_pixels=50 y_pixels=20 
			center=14.100000 bandwidth=0.200000 min_dbm=-135.00 max_dbm=-40.00 fps=25 average=50 weighted_average=0 rfgain=0 rxant=ANT1 wide=0 
			loopa=0 loopb=0 band=20 daxiq_channel=0 waterfall=0x42000000 min_bw=0.004920 max_bw=7.372800 xvtr= pre= ant_list=ANT1,ANT2,RX_A,XVTA 
			"""




def ParseMessage(radio, string):
	try:
		(MessageNum, rec_msg) = string.split('|')
	except ValueError:
		print("Error - Invalid message")
		return

	# add rec_msg to log - logging.addMessage()


""" redundant? """
def ParseHandle(radio, string):
	if len(string) >= 8:
		radio.ClientHandle = string[1:9]
	else:
		print("Error - Invalid handle returned")


def ParseVersion(radio, string):
	radio.clientHandle = string.split('H')[1].strip()
	print("New Client Handle: " + radio.clientHandle)


def ParseVitaPacket(radio, packet):
	Id = int.from_bytes(packet.class_id, byteorder='big') & int('FFFF',16)	# all but the last 2 bytes are the same
	if Id == int('FFFF',16):
		# DISCOVERY Packet
		pass
	elif Id == int('8003',16):
		# FFT Packet
		print("FFT:", packet.pkt_size, len(packet.payload))
		if radio.Panafall:
			pan_data = ParsePanadapterPacket(packet, radio.Panafall.x_pixels, radio.Panafall.y_pixels)
			radio.Panafall.PanBuffer.put_nowait(pan_data)
	elif Id == int('8004',16):
		# WATERFALL Packet:
		ParseWaterfallPacket(packet)
	elif Id == int('8005',16):
		# OPUS AUDIO Packet
		opusData = ParseOpusPacket(packet)
		if radio.RxAudioStreamer:
			radio.RxAudioStreamer.outBuffer.put_nowait(opusData)
	elif Id == int('3E3',16):
		# IF NARROW Packet
		rawData = ParseIfNarrowPacket(packet)
		if radio.RxAudioStreamer:
			for flt in iter_unpack("!f",rawData):	# take every 4 bytes and cast to IEEE float
				radio.RxAudioStreamer.outBuffer.put_nowait(flt[0])	# iter_unpack returns tuple of 1 item


def ParseOpusPacket(packet):
	return packet.payload
	# return data[:len(data)-preamble.Header.Payload_cutoff_bytes]


def ParseIfNarrowPacket(packet):
	return packet.payload


def ParseWaterfallPacket(packet):
	#do something
	pass

def ParsePanadapterPacket(packet, x, y):
	# for item in iter_unpack(">H", packet.payload):
	pan_data = [] 
	index = 0

	StartBin_index = unpack(">H", packet.payload[index : index+2])[0]
	index += 2

	NumBins = unpack(">H", packet.payload[index : index+2])[0]
	index += 2

	BinSize = unpack(">H", packet.payload[index : index+2])[0]
	index += 2

	TotalBinsInFrame = unpack(">H", packet.payload[index : index+2])[0]
	index += 2

	FrameIndex = unpack(">L", packet.payload[index : index+4])[0]
	index += 4

	for i in range(0,int(NumBins)*2,2):
		pan_data.append( unpack(">H", packet.payload(data[i+index:i+index+2]))[0] )

	return pan_data




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



