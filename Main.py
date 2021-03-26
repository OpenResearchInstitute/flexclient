import http.client, pdb, socket, ssl, threading, select
from time import sleep          # Needed to prevent busy-waiting for the browser to complete the login process!
from pkg.Initialiser import ConnectRadio
from pkg.SmartLink import SmartLink
from pkg.Radio import Radio
from pkg.Slice import Slice
import pkg.DataHandler

SERIAL = '1019-9534-6400-6018'  # should be set through user input at startup


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
		# flexRadio.FLEX_Sock.send("version\n".encode("cp1252"))
		# sleep(1)

		flexRadio.SendCommand("slice list")
		# flexRadio.SendCommand("ant list")
		sleep(1)
		flexRadio.AddSlice(3.55, 'RX_A', 'lsb')
		flexRadio.SendCommand('sub slice all')
		# sleep(1)
		# flexRadio.GetSlice(0).Tune(10)
		sleep(1)
		flexRadio.SendCommand("slice list")
		sleep(1)
		
		flexRadio.CreateAudioStream()
		flexRadio.OpenUDPConnection()

		pdb.set_trace()

		flexRadio.GetSlice(0).Remove()
		sleep(1)
		receiveThread.running = False
		flexRadio.CloseRadio()
		smartlink.CloseLink()
		

	else:
		print("Connection Unsuccessful")



if __name__ == "__main__":
	main()

