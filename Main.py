import http.client, pdb, socket, ssl, threading, select
from time import sleep          # Needed to prevent busy-waiting for the browser to complete the login process!
from FlexModule.SmartLink import SmartLink
from FlexModule.Radio import Radio
import FlexModule.DataHandler
import numpy, time

SERIAL = '1019-9534-6400-6018'  # should be set through user input at startup


def main():
	""" smartlink connection should stay open if user wants to interact with multiple radios """
	# SERIAL = input("\nEnter your radio's Serial Number: ")
	smartlink = SmartLink()
	radioInfo = smartlink.GetRadioFromAvailable(SERIAL)
	flexRadio = Radio(radioInfo, smartlink)
	if flexRadio.serverHandle:
		receiveThread = FlexModule.DataHandler.ReceiveData(flexRadio)
		receiveThread.start()

		sleep(2)

		# print("sending version command")
		# flexRadio.FLEX_Sock.send("version\n".encode("cp1252"))

		flexRadio.UpdateAntList()
		flexRadio.SendCommand('sub slice all')
		flexRadio.GetSliceList()
		flexRadio.SendCommand("sub pan all")
		
		flexRadio.CreateAudioStream(False)
		while not flexRadio.RxAudioStreamer:
			continue
		flexRadio.OpenUDPConnection()

		sleep(3)
		print("Stream Buffer: ", len(flexRadio.RxAudioStreamer.outBuffer))
		flexRadio.GetSlice(0).Tune(7.5)
		sleep(3)
		print("Stream Buffer: ", len(flexRadio.RxAudioStreamer.outBuffer))
		flexRadio.GetSlice(0).Remove()

		start = time.process_time()
		gnuBuf = numpy.array([])
		# while not flexRadio.RxAudioStreamer.outBuffer.empty():
		# 	numpy.append(gnuBuf, flexRadio.RxAudioStreamer.outBuffer.get_nowait())
		temp = numpy.array()
		out[:] = temp
		print(time.process_time() - start)


		flexRadio.RxAudioStreamer.Close()



		receiveThread.running = False
		flexRadio.CloseRadio()
		smartlink.CloseLink()
		
	else:
		print("Connection Unsuccessful")



if __name__ == "__main__":
	main()

