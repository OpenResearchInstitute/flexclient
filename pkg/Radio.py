import http.client, pdb, socket, ssl, threading, select


class Radio(object):
	""" Class to create connection with FLEX radio and establish communication channel """
	def __init__(self, radioData, smartlink):
		self.smartlink_sock = smartlink.wrapped_server_sock
		self.radioData = radioData
		context = ssl.create_default_context()
		context.check_hostname = False
		context.verify_mode = ssl.CERT_NONE
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.FLEX_Sock = ssl.wrap_socket(self.sock)

		self.serverHandle = self.SendConnectMessageToRadio()
		self.FLEX_Sock.connect((self.radioData['public_ip'], int(self.radioData['public_upnp_tls_port'])))
		print(self.FLEX_Sock.getpeername())
		if self.serverHandle:
			self.WanValidate()


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


	def SendCommand(self, string):
		print(string)
		command = (string + "\n").encode("cp1252")
		self.FLEX_Sock.send(command)


	def CloseRadio(self):
		self.SendCommand("client disconnect " + self.serverHandle)
		self.FLEX_Sock.close()
		self.sock.close()



