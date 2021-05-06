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
					if self.radio.UdpListening:
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
			pan_info = dict(param.split("=") for param in sent_msg.split(" ")[4:])
			for key, value in pan_info.items():
				# For some reason, the radio expects a different term to one it returns for these two ¯\_(ツ)_/¯
				if key == "xpixels":
					setattr(radio.Panafall, "x_pixels", float(value))
				elif key == "ypixels":
					setattr(radio.Panafall, "y_pixels", float(value))
				else:
					try:
						val_type = type(getattr(radio.Panafall, key))
					except AttributeError:
						continue

					if val_type is float or val_type is int:
						setattr(radio.Panafall, key, float(value))
					else:
						setattr(radio.Panafall, key, value)
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
	ValidatePacketCount(Id, packet.pkt_count)
	# print(Id, packet.pkt_count)
	if Id == int('FFFF',16):
		# DISCOVERY Packet
		pass
	elif Id == int('8003',16):
		# FFT Packet
		# print("FFT:", packet.pkt_size, len(packet.payload))
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
		if radio.RxAudioStreamer:
			ParseIfNarrowPacket(packet, radio.RxAudioStreamer.outBuffer)
		# rawData = ParseIfNarrowPacket(packet)
		# if radio.RxAudioStreamer:
		# 	switch = True
		# 	for flt in iter_unpack("!f",rawData):	# take every 4 bytes and cast to IEEE float
		# 		# FLEX sends 2 channels of same audio stream - I'm only saving 1 channel
		# 		if switch:
		# 			radio.RxAudioStreamer.outBuffer.put_nowait(flt[0])	# iter_unpack returns tuple of 1 item
		# 		# else:
		# 		# 	do something here if 2nd channel required
		# 		switch ^= 1


def ParseOpusPacket(packet):
	return packet.payload
	# return data[:len(data)-preamble.Header.Payload_cutoff_bytes]


def ParseIfNarrowPacket(packet, buffer):
	switch = True
	# cast to list() to be able to index
	for flt in iter_unpack("!f", packet.payload):	# take every 4 bytes and cast to float
		# FLEX sends 2 channels of same audio stream - I'm only saving 1 channel
		if switch:
			buffer.put_nowait(flt[0])	# iter_unpack returns tuple of 1 item
		# else:
		# 	do something here if 2nd channel required
		switch = not switch


def ParseWaterfallPacket(packet):
	"""
To render the waterfall, you need to:
Map the pixel offset in the display to a frequency using the pan adaptor settings as reference.  In the above example, pixel zero in the pan adaptor is 14.000 and pixel one is 14.0001953125 etc.
Find the nearest "bin" at or below this frequency, interpolate the "bin" values of adjacent bins to determine the appropriate magnitude for this pixel frequency.
Map the 16 bit unsigned integer value into an appropriate color space.
Set the corresponding X pixel in the bitmap to this color.
This needs to be done for each line in the bitmap which is rendered from the list of tiles received - with each update you draw the top line of the bitmap and scroll all the older lines down by one pixel vertically.

	index := 0

	wftile.FrameLowFreq = binary.BigEndian.Uint64(data[index:8]) >> 20	# NEED
	index += 8

	wftile.BinBandwidth = binary.BigEndian.Uint64(data[index:index+8]) >> 20	# NEED
	index += 8

	wftile.MysteryValue = binary.BigEndian.Uint16(data[index : index+2])
	index += 2

	wftile.LineDurationMS = binary.BigEndian.Uint16(data[index : index+2])
	index += 2

	wftile.Width = binary.BigEndian.Uint16(data[index : index+2])	# MAYBE
	index += 2

	wftile.Height = binary.BigEndian.Uint16(data[index : index+2])	# MAYBE
	index += 2

	wftile.Timecode = binary.BigEndian.Uint32(data[index : index+4])
	index += 4

	wftile.AutoBlackLevel = binary.BigEndian.Uint32(data[index : index+4])
	index += 4

	wftile.TotalBinsInFrame = binary.BigEndian.Uint16(data[index : index+2])	# MAYBE
	index += 2

	wftile.FirstBinIndex = binary.BigEndian.Uint16(data[index : index+2])	# MAYBE
	index += 2

	for i := 0; i < (len(data))-preamble.Header.Payload_cutoff_bytes-index-4; /* -4 should not be.... another mytery*/ i += 2 {
		wftile.Data = append(wftile.Data, binary.BigEndian.Uint16(data[i+index:i+index+2]))
	}
	"""
	pass

def ParsePanadapterPacket(packet, x, y):
	pan_data = [] 
	index = 0

	StartBin_index, NumBins, BinSize, TotalBinsInFrame, FrameIndex, Packet_Count = unpack(">HHHHLL", packet.payload[index:index+16])
	# Packet_Count could be used to error check, but we already have an error check for all VITA packet types
	index += 16

	for i in iter_unpack(">H", packet.payload[index:index+TotalBinsInFrame*2]):
		pan_data.append(y - i[0])	# invert y axis as FLEX graphs differently 

	return pan_data


def ValidatePacketCount(pkt_id, pkt_cnt):
	Error = False
	if pkt_cnt == 0:
		prev_cnt = 15
	else: prev_cnt = pkt_cnt - 1

	if pkt_id == int('8003',16):
		try:
			if ValidatePacketCount.fftCount != prev_cnt:
				Error = True
		except AttributeError:
			# not been intialised yet, will be below
			pass
		ValidatePacketCount.fftCount = pkt_cnt
	elif pkt_id == int('8004',16):
		try:
			if ValidatePacketCount.wtrflCount != prev_cnt:
				Error = True
		except AttributeError:
			pass
		ValidatePacketCount.wtrflCount = pkt_cnt
	elif pkt_id == int('8005',16):
		try:
			if ValidatePacketCount.opusCount != prev_cnt:
				Error = True
		except AttributeError:
			pass
		ValidatePacketCount.opusCount = pkt_cnt
	elif pkt_id == int('3E3',16):
		try:
			if ValidatePacketCount.ifNCount != prev_cnt:
				Error = True
		except AttributeError:
			pass
		ValidatePacketCount.ifNCount = pkt_cnt
	# Add more packet types when required 

	if Error:
		print("D", end="")



