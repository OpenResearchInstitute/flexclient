import http.client, pdb, socket, ssl, threading, select
from time import sleep          # Needed to prevent busy-waiting for the browser to complete the login process!
from pkg.Initialiser import ConnectRadio
from pkg.SmartLink import SmartLink
from pkg.Radio import Radio
from pkg.Slice import Slice
import pkg.DataHandler

SERIAL = '1019-9534-6400-6018'  # should be set through user input at startup
# CLIENT_HANDLE = '' # changes every session, set during initialisation


# def main():
# 	# SERIAL = input("\nEnter your radio's Serial Number:")

# 	print("Using browser-based authentication...\n")
# 	myRadio = ConnectRadio(SERIAL)

# 	if myRadio.FLEX_Sock:
# 		myRadio.WanValidate(myRadio.FLEX_Sock, myRadio.Handle)
# 		print('\n\nCommunication with FLEX:')
# 		receiveThread = pkg.DataHandler.ReceiveData(myRadio.FLEX_Sock)
# 		receiveThread.start()


# 		sleep(2)

# 		print("sending version command")
# 		myRadio.FLEX_Sock.send("C1|version\n".encode("cp1252"))
# 		sleep(1)

# 		myRadio.SendCommand("C41|slice list")
# 		sleep(1)

# 		slice1 = Slice(myRadio, 10, 'ANT1', 'am')
# 		sleep(1)

# 		myRadio.SendCommand("C41|slice list")

# 		sleep(2)
# 		pdb.set_trace()

# 		"""while True:
# 			# read replies from replies_buffer
# 			# update statuses from statuses_buffer
# 			# requires another input thread?
# 			cmd = input('Enter a command:')
# 			if cmd == "exit":
# 				break
# 			else:
# 				SendCommand(myRadio.FLEX_Sock, cmd)
# 			sleep(2)"""
		
# 		myRadio.SendCommand("client disconnect " + myRadio.Handle)
# 		sleep(2)
# 		myRadio.FLEX_Sock.close()
# 	else:
# 		print("Connection to Radio Failed")


def main():
	""" smartlink connection should stay open if user wants to interact with multiple radios """
	# SERIAL = input("\nEnter your radio's Serial Number: ")
	smartlink = SmartLink()
	radioInfo = smartlink.GetRadioFromAvailable(SERIAL)
	flexRadio = Radio(radioInfo, smartlink)
	if flexRadio.serverHandle:
		receiveThread = pkg.DataHandler.ReceiveData(flexRadio)
		receiveThread.start()

		sleep(2)

		# print("sending version command")
		# flexRadio.FLEX_Sock.send("C1|version\n".encode("cp1252"))
		# sleep(1)

		flexRadio.SendCommand("C41|slice list")
		# flexRadio.SendCommand("C16|ant list")
		sleep(1)
		flexRadio.AddSlice(3.55, 'RX_A', 'lsb')
		sleep(1)
		flexRadio.SendCommand("C41|slice list")
		sleep(1)
		flexRadio.CreateAudioStream()
		pdb.set_trace()
		flexRadio.OpenUDPConnection()

		pdb.set_trace()

		flexRadio.GetSlice(0).Remove()
		receiveThread.running = False
		flexRadio.CloseRadio()
		smartlink.CloseLink()
		

	else:
		print("Connection Unsuccessful")



if __name__ == "__main__":
	main()

"""
1) Sent "slice create freq=3.550000 rxant=RX_A mode=LSB" to the radio
via TLS (don't forget to remove it with "slice remove <index>" later!),
2) Send "stream create type=remote_audio_rx compression=opus" to the
radio via TLS; this resulted in a client_handle being returned to me (if
creation of the stream was successful),
3) Opened a UDP connection to the radio on the public UDP port (22000
currently),
4) Sent "client udp_register handle=<client_handle>" _VIA THAT NEW UDP
CONNECTION_ to the radio (note there is no newline at the end of this
command!)

"""