import http.client, pdb, socket, ssl, threading, select
from time import sleep          # Needed to prevent busy-waiting for the browser to complete the login process!
from FlexModule.SmartLink import SmartLink
from FlexModule.Radio import Radio
import FlexModule.DataHandler
import numpy, time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

SERIAL = '1019-9534-6400-6018'  # should be set through user input at startup
smartlink = SmartLink()
radioInfo = smartlink.GetRadioFromAvailable(SERIAL)
flexRadio = Radio(radioInfo, smartlink)

def animate(i):
	plt.cla()
	plt.xlim([0,flexRadio.Panafall.x_pixels])
	plt.ylim([0,flexRadio.Panafall.y_pixels])
	plt.plot(flexRadio.Panafall.PanBuffer.get_nowait())


def main():
	""" smartlink connection should stay open if user wants to interact with multiple radios """
	# SERIAL = input("\nEnter your radio's Serial Number: ")
	
	if flexRadio.serverHandle:
		receiveThread = FlexModule.DataHandler.ReceiveData(flexRadio)
		receiveThread.start()

		# sleep(2)
		flexRadio.UpdateAntList()
		flexRadio.SendCommand('sub slice all')
		flexRadio.GetSliceList()
		flexRadio.SendCommand("sub pan all")
		
		# sleep(2)
		flexRadio.GetSlice(0).Tune(14.222)
		flexRadio.SendCommand("slice t 0 14.222 autopan=1")
		flexRadio.GetSlice(0).Set(mode='USB', rxant="ANT2")
		# pdb.set_trace()
		flexRadio.CreateAudioStream(False)
		sleep(1)
		flexRadio.OpenUDPConnection()
		
		# """ Audio Stream Test """
		testTime = 10 #seconds
		sampRate = 24000
		bytesPerSamp = 4
		sleep(10)
		flexRadio.CloseUDPConnection()
		noOfBytes = flexRadio.RxAudioStreamer.outBuffer.qsize() * bytesPerSamp
		expectedBytes = testTime * sampRate * bytesPerSamp
		print("\nReceived Bytes:", noOfBytes, "\tExpected Bytes",  expectedBytes)
		flexRadio.RxAudioStreamer.WriteToFile()

		# pdb.set_trace()

		receiveThread.running = False
		flexRadio.CloseRadio()
		smartlink.CloseLink()
		
	else:
		print("Connection Unsuccessful")



if __name__ == "__main__":
	main()

