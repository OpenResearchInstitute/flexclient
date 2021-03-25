import http.client, pdb, socket, ssl, threading, select
from pkg.Slice import Slice


class Radio(object):
	""" Class to create connection with FLEX radio and establish communication channel """
	def __init__(self, radioData, smartlink):
		self.smartlink_sock = smartlink.wrapped_server_sock	# socket to comms with Smartlink
		self.radioData = radioData	# info for the radio about itself
		context = ssl.create_default_context()
		context.check_hostname = False
		context.verify_mode = ssl.CERT_NONE
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.FLEX_Sock = ssl.wrap_socket(self.sock)	# socket to comms with the FLEX radio
		self.DATA_Sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.clientHandle = ""
		self.serverHandle = self.SendConnectMessageToRadio()
		if self.serverHandle:
			self.FLEX_Sock.connect((self.radioData['public_ip'], int(self.radioData['public_upnp_tls_port'])))
			print(self.FLEX_Sock.getpeername())
			self.WanValidate()

		self.ResponseList = []
		self.StatusList = []
		self.antList = []
		self.sliceList = []


	def SendConnectMessageToRadio(self):
		try:
			command = "application connect serial=" + self.radioData['serial'] + " hole_punch_port=" + str(self.radioData['public_upnp_tls_port']) + "\n"
		except TypeError:
			print("Radio Serial not returned - is radio On?")
			return
		print("\nSending connect message: " + command)
		self.smartlink_sock.send(command.encode("cp1252"))
		handle_data = self.smartlink_sock.recv(128).decode("cp1252")
		print(handle_data)
		try:
			handle = handle_data.split('handle=')[1].strip()
			return handle
		except IndexError:
			print("Server Handle not received")
			return ""


	def WanValidate(self):
		command = "C1|wan validate handle=" + self.serverHandle + "\n"
		print("\nSending Wan Validate command: " + command + "\n")
		self.FLEX_Sock.send(command.encode("cp1252"))


	def OpenUDPConnection(self):
		command = "client udp_register handle=0x" + self.clientHandle
		self.DATA_Sock.sendto(command.encode("cp1252"), (self.radioData["public_ip"], int(self.radioData["public_upnp_udp_port"])))


	def SendCommand(self, string):
		print(string)
		command = (string + "\n").encode("cp1252")
		self.FLEX_Sock.send(command)


	def CreateAudioStream(self):
		command = "C19|stream create type=remote_audio_rx compression=opus"
		self.SendCommand(command)


	def AddSlice(self, freq, ant, mode):
		# if ant in self.antList:
		self.sliceList.append(Slice(self, freq, ant, mode))
		# else:
		# 	raise Exception("Chosen Antenna not available")

		# add reply expected to reply list = R21|0|0

	def GetSlice(self, s_id):
		""" We want the slice with corresponding id (as this is what FLEX recognises) """
		return [s for s in self.sliceList if s.slice_id == s_id][0]

	def RemoveSlice(self, slice_id):
		GetSlice(slice_id).Remove()


	def CloseRadio(self):
		self.SendCommand("client disconnect " + self.serverHandle)
		self.FLEX_Sock.close()
		self.sock.close()



