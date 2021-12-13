#!/bin/env python
# import pdb, socket, ssl, threading, select
import socket
from flexclient.LAN import LANDiscovery

from flexclient.Radio import Radio
import flexclient.DataHandler
import time
from sys import exit
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

SERIAL = os.getenv("FLEX_SERIAL_NUMBER") or None
if SERIAL is None:
    print("Environment variable FLEX_SERIAL_NUMBER not found")
    exit()

# If we must authenticate using smartlink, then we can get a list
# os accessible radios
discovery = LANDiscovery()
time.sleep(2)  # radios broadcast discovery every second

radioInfo = discovery.GetRadioFromAvailable(SERIAL)
if radioInfo is None:
    print("Failed to retrieve Radio Info, exiting")
    exit()

print("main")
# print(radioInfo)
flexRadio = Radio(radioInfo, None)


def animate(i):
    plt.cla()
    plt.xlim([0, flexRadio.Panafall.x_pixels])
    plt.ylim([0, flexRadio.Panafall.y_pixels])
    plt.plot(flexRadio.Panafall.PanBuffer.get_nowait())


def main():
    """smartlink connection should stay open if user wants to interact with multiple radios"""
    # SERIAL = input("\nEnter your radio's Serial Number: ")

    if True or flexRadio.serverHandle:
        receiveThread = flexclient.DataHandler.ReceiveData(flexRadio)
        receiveThread.start()

        # sleep(2)
        print("Before subscriptions are enabled:")
        print("Slice frequency: ", flexRadio.GetSlice(0).RF_frequency)
        print("Slice demodulation mode: ", flexRadio.GetSlice(0).mode)
        flexRadio.UpdateAntList()
        flexRadio.SendCommand("sub slice all")
        flexRadio.GetSliceList()
        flexRadio.SendCommand("sub pan all")

        # sleep(2)
        # flexRadio.GetSlice(0).Tune(14.222)
        # flexRadio.SendCommand("slice t 0 14.222 autopan=1")
        # flexRadio.GetSlice(0).Set(mode='USB', rxant="ANT2")
        # pdb.set_trace()
        # flexRadio.CreateAudioStream(False)
        # flexRadio.Panafall.Set(xpixels=1000)
        # flexRadio.Panafall.Set(ypixels=700)
        # flexRadio.Panafall.Set(rxant="ANT2")
        # flexRadio.Panafall.Set(rfgain=0.9)
        time.sleep(1)
        print("After subscriptions are enabled:")
        print("Slice frequency: ", flexRadio.GetSlice(0).RF_frequency)
        print("Slice demodulation mode: ", flexRadio.GetSlice(0).mode)
        # flexRadio.OpenUDPConnection()
        # sleep(1)

        # """ Audio Stream Test """
        # testTime = 10 #seconds
        # sampRate = 24000
        # bytesPerSamp = 4
        # sleep(10)
        # flexRadio.CloseUDPConnection()
        # noOfBytes = flexRadio.RxAudioStreamer.outBuffer.qsize() * bytesPerSamp
        # expectedBytes = testTime * sampRate * bytesPerSamp
        # print("\nReceived Bytes:", noOfBytes, "\tExpected Bytes",  expectedBytes)
        # flexRadio.RxAudioStreamer.WriteToFile()

        """ Pan Adapter Plot test """
        # ani = FuncAnimation(plt.gcf(), animate, interval=42)
        # plt.tight_layout()
        # plt.show()

        # pdb.set_trace()

        receiveThread.running = False
        flexRadio.CloseRadio()

    else:
        print("Connection Unsuccessful")


if __name__ == "__main__":
    main()