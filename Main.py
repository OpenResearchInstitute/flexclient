import http.client, pdb, socket, ssl, threading, select
from time import sleep          # Needed to prevent busy-waiting for the browser to complete the login process!

SERIAL = '1019-9534-6400-6018'  # should be set through user input at startup
CLIENT_HANDLE = '' # changes every session, set during initialisation

class ReceiveData(threading.Thread):
	""" Thread to contiually receive tcp data in BG """
	def __init__(self, socket):
		threading.Thread.__init__(self, daemon=True)
		self.socket = socket

	def run(self):
		read_socks = [self.socket]
		while read_socks:
			readable, w, e = select.select(read_socks,[],[],0)
			for s in readable:
				data = s.recv(512).decode("cp1252")
				if data:
					# ParseRead(data)
					print(data)
				else:
					read_socks.remove(s)


def main():
  # SERIAL = input("\nEnter your radio's Serial Number:")

	print("Using browser-based authentication...\n")
	myRadio = Initialise(SERIAL)
	FLEX = myRadio.FLEX_Sock

	if FLEX:
		print('\n\nCommunication with FLEX:')
		# WanValidate(FLEX, ServerHandle)
		receiveThread = ReceiveData(FLEX)
		receiveThread.start()


		sleep(5)

		print("sending version command")
		FLEX.send("C1|version\n".encode("cp1252"))
		sleep(5)

		# print("sending antenna_list request")
		# FLEX_Sock.send("C16|ant list\n".encode("cp1252"))
		# sleep(5)

		"""
		while True:
			read replies from replies_buffer
			update statuses from statuses_buffer
			# requires another input thread
			if input == exit:
			break
		"""
		FLEX.close()
	else:
		print("Connection to Radio Failed")


if __name__ == "__main__":
	main()
