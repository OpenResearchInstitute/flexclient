import http.client, pdb, socket, ssl, threading, select
from time import sleep          # Needed to prevent busy-waiting for the browser to complete the login process!
from pkg.Initialiser import ConnectRadio
from pkg.SmartLink import SmartLink
from pkg.Radio import Radio
from pkg.Slice import Slice
import pkg.DataHandler

SERIAL = '1019-9534-6400-6018'  # should be set through user input at startup
CLIENT_HANDLE = '' # changes every session, set during initialisation


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
# 		sleep(2)

# 		print("sending antenna_list request")
# 		myRadio.SendCommand("C16|ant list")

# 		slice1 = Slice(myRadio, 10, 'ANT1', 'am')

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

	receiveThread = pkg.DataHandler.ReceiveData(flexRadio.FLEX_Sock)
	receiveThread.start()

	sleep(2)

	print("sending version command")
	flexRadio.FLEX_Sock.send("C1|version\n".encode("cp1252"))
	sleep(2)

	print("sending antenna_list request")
	flexRadio.SendCommand("C16|ant list")

	pdb.set_trace()

	flexRadio.CloseRadio()
	smartlink.CloseLink()






if __name__ == "__main__":
	main()

