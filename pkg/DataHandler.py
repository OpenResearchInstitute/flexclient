import http.client, pdb, socket, ssl, threading, select


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
					print(udpResponse)

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


	radio.ResponseList.pop(response_code)


def ParseStatus(radio, string):
	try:
		(radio_handle, rec_msg) = string.split('|')
	except ValueError:
		print("Error - Invalid status message")
		return

	if radio_handle == "S" + radio.clientHandle:  # status message for this client i.e you
		if rec_msg.startswith("slice"):
			s_id = int(rec_msg[6])
			# print(rec_msg+"\n")
			slice_info = dict(param.split("=") for param in rec_msg[8:].split(" "))
			# print(slice_info)
			try:
				radio.GetSlice(s_id).freq = float(slice_info["RF_frequency"])
				radio.GetSlice(s_id).mode = slice_info["mode"]
				radio.GetSlice(s_id).ant = slice_info["rxant"]
			except KeyError:
				pass
		elif rec_msg.startswith("radio"):
			pass



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


