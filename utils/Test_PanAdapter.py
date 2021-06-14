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
	data = flexRadio.Panafall.PanBuffer.get_nowait()
	xaxis = numpy.linspace(flexRadio.Panafall.center - (flexRadio.Panafall.bandwidth/2), flexRadio.Panafall.center + (flexRadio.Panafall.bandwidth/2), len(data))
	plt.xlim(xaxis[0], xaxis[-1])
	plt.ylim([flexRadio.Panafall.min_dbm,flexRadio.Panafall.max_dbm])
	plt.title("Panadapter Plot")
	plt.xlabel("Frequency (MHz)")
	plt.ylabel("Amplitude (dB)")
	plt.plot(xaxis, data)


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
		flexRadio.Panafall.Set(xpixels=1000)
		flexRadio.Panafall.Set(ypixels=700)
		flexRadio.Panafall.Set(rxant="ANT2")
		flexRadio.Panafall.Set(rfgain=0.9)
		flexRadio.OpenUDPConnection()
		sleep(1)
		

		""" Pan Adapter Plot test """
		ani = FuncAnimation(plt.gcf(), animate, interval=42)
		plt.tight_layout()
		plt.show()

		# pdb.set_trace()

		receiveThread.running = False
		flexRadio.CloseRadio()
		smartlink.CloseLink()
		
	else:
		print("Connection Unsuccessful")



if __name__ == "__main__":
	main()

