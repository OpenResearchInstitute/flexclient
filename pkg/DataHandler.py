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
						ParseRead(self.radio, tcpResponse)
						tcpResponse = ""
				elif s.type == 2: # "SOCK_DGRAM"
					udpResponse = s.recvfrom(1024)
					print(udpResponse)

				# if not data:
				# 	read_socks.remove(s)
			if not self.running:
				read_socks.clear()




def ParseRead(radio, string):
	print(string)
	read_type = string[0]
	if read_type == "R":
		ParseReply(radio, string)
	elif read_type == "S":
		ParseStatus(radio, string)
	elif read_type == "M":
		ParseMessage(radio, string)
	elif read_type == "H":
		ParseHandle(radio, string)
	elif read_type == "V":
		ParseVersion(radio, string)
	# else:
	# 	print("Unknown response from radio: " + radio.radioData["serial"]) 


def ParseReply(radio, string):
	try:
		(response_code, hex_code, msg) = string.split('|')
	except ValueError:
		print("Error - Incomplete reply")
		return

	# if int(hex_code) == 0:  # msg reponse is "OK"
		# Remove {reponse_code: msg} to radio.ResponseList[]


def ParseStatus(radio, string):
	try:
		(radio_handle, msg) = string.split('|')
	except ValueError:
		print("Error - Invalid status message")
		return

	# if radio_handle == s + radio.ClientHandle:  # status message for this client i.e you
		# Update radio settings OR Remove status from radio.StatusList[]


def ParseMessage(radio, string):
	try:
		(MessageNum, msg) = string.split('|')
	except ValueError:
		print("Error - Invalid message")
		return

	# add msg to log - logging.addMessage()

""" redundant? """
def ParseHandle(radio, string):
	if len(string) >= 8:
		radio.ClientHandle = string[1:9]
	else:
		print("Error - Invalid handle returned")


def ParseVersion(radio, string):
	radio.clientHandle = string.split('H')[1].strip()
	print("New Client Handle: " + radio.clientHandle)


