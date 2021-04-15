import http.client, pdb, socket, ssl, threading, select
from .Vita import VitaPacket
from .RxRemoteAudioStream import RxRemoteAudioStream
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



class WriteData(threading.Thread):
	""" Thread to send data to GNU Radio in BG """
	def __init__(self, radio):
		threading.Thread.__init__(self, daemon=True)
		self.radio = radioData
		self.running = True

	def run(self):
		write_socks = []	# GNU Port buffer
		""" 
		while socket is open: OR while self.running:
			for i in len(outBuffer):
				socket.send(outBuffer.get_nowait(), GNU_RADIO_UDP_ADDR)
		"""




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
	hex_code = int(hex_code)
	# rec_msg = rec_msg.strip()
	try:
		sent_msg = radio.ResponseList[response_code]
	except ValueError:
		print('Unexpected reply')
	
	if "slice create" in sent_msg:
		if hex_code != 0:
			# log error
			pass
	elif "slice r" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		# remove self now that radio has confirmed deletion
		s_id = int(sent_msg[-1])
		radio.SliceList.remove(radio.GetSlice(s_id))
	elif "slice list" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		# radio.SliceList = rec_msg.split(sep=" ") # HOW TO USE |0 1 to update Slicelist??
	elif "ant list" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		radio.AntList = rec_msg.split(sep=",")
	elif "stream create" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		if "type=remote_audio_rx" in sent_msg:
			streamCompression = sent_msg.split("compression=")[1]
			if streamCompression == "opus":
				radio.RxAudioStreamer = RxRemoteAudioStream(radio, rec_msg, True)
			else:
				radio.RxAudioStreamer = RxRemoteAudioStream(radio, rec_msg, False)
	elif "stream remove" in sent_msg:
		if hex_code != 0:
			# log error
			pass
		# s_id = sent_msg.split("remove 0x")[1]
		radio.RxAudioStreamer = None



	radio.ResponseList.pop(response_code)


def ParseStatus(radio, string):
	try:
		(radio_handle, rec_msg) = string.split('|')
	except ValueError:
		print("Error - Invalid status message")
		return

	if radio_handle == "S" + radio.clientHandle:  # status message for this client i.e you
		if rec_msg.startswith("slice"):
			split_msg = rec_msg.split(sep=' ', maxsplit=2)
			s_id = int(split_msg[1])
			slice_info = dict(param.split("=") for param in split_msg[2].split(" "))
						
			try:
				radio.GetSlice(s_id).freq = float(slice_info["RF_frequency"])
			except KeyError:
				pass
			try:
				radio.GetSlice(s_id).mode = slice_info["mode"]
			except KeyError:
				pass
			try:
				radio.GetSlice(s_id).ant = slice_info["rxant"]
			except KeyError:
				pass
			""" is there a nicer more pythonic way to do this ^ ? """
		elif rec_msg.startswith("radio"):
			pass
		elif rec_msg.startswith("display pan"):
			# print(rec_msg)
			split_msg = rec_msg.split(sep=' ', maxsplit=3)
			p_id = split_msg[2]
			pan_info = dict(param.split("=") for param in split_msg[3].split(" "))

			# try:
			# 	radio.GetPanAdapter(p_id).center = float(pan_info["center"])
			# except KeyError:
			# 	pass
			# try:
			# 	radio.GetPanAdapter(p_id).bandwidth = float(pan_info["bandwidth"])
			# except KeyError:
			# 	pass
			# try:
			# 	radio.GetPanAdapter(p_id).x_pixels = int(pan_info["x_pixels"])
			# except KeyError:
			# 	pass
			# try:
			# 	radio.GetPanAdapter(p_id).y_pixels = int(pan_info["y_pixels"])
			# except KeyError:
			# 	pass
			# try:
			# 	radio.GetPanAdapter(p_id).fps = int(pan_info["fps"])
			# except KeyError:
			# 	pass
			# try:
			# 	radio.GetPanAdapter(p_id).daxiq_channel = int(pan_info["daxiq_channel"])
			# except KeyError:
			# 	pass
			# try:
			# 	radio.GetPanAdapter(p_id).rxant = int(pan_info["rxant"])
			# except KeyError:
			# 	pass




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



# def GetSubscriptionInfo(subString, desiredTxt):
# 		""" retrieve necessary radio info """
# 		subString = subString.split(' ')
# 		slice_id = subString[1]
# 		for param in subString:
# 			for txt in desiredTxt.keys():	# need exact match not string.contain i.e "mode" is also in "agc_mode"
# 				if (txt + "=") in param:
# 					desiredTxt[txt] = param.split('=')[1]

# 		# pdb.set_trace()
# 		return slice_id, desiredTxt


def ParseVitaPacket(radio, packet):
	Id = int.from_bytes(packet.class_id, byteorder='big') & int('FFFF',16)	# all but the last 2 bytes are the same
	# print("Packet Id: ", Id)
	# print("Packet Size: ", packet.pkt_size)
	if Id == int('FFFF',16):
		# DISCOVERY Packet
		pass
	elif Id == int('8003',16):
		# FFT Packet
		pass
	elif Id == int('8005',16):
		# OPUS AUDIO Packet
		opusData = ParseOpusPacket(packet)
		print("OPUS data: \n", opusData, "\n")
		if radio.RxAudioStreamer:
			radio.RxAudioStreamer.outBuffer.put_nowait(opusData)
			# radio.RxAudioStreamer.outBuffer.append(opusData)
	elif Id == int('3E3',16):
		# IF NARROW Packet
		rawData = ParseIfNarrowPacket(packet)
		# print("IF-NARROW data \n:", rawData, "\n")
		if radio.RxAudioStreamer:
			for flt in iter_unpack("<f",rawData):	# take every 4 bytes and cast to float
				radio.RxAudioStreamer.outBuffer.put_nowait(flt[0])	# iter_unpack returns tuple of 1 item
				# radio.RxAudioStreamer.outBuffer.append(flt[0])


def ParseOpusPacket(packet):
	return packet.payload
	# return data[:len(data)-preamble.Header.Payload_cutoff_bytes]


def ParseIfNarrowPacket(packet):
	return packet.payload


