#!/bin/env python
# import pdb, socket, ssl, threading, select
import socket
from flexclient.LAN import LANDiscovery

# from flexclient.Radio import Radio
# import flexclient.DataHandler
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

while True:
    time.sleep(2.4)


radioInfo = smartlink.GetRadioFromAvailable(SERIAL)
if radioInfo is None:
    print("Failed to retrieve Radio Info, exiting")
    exit()

print("main")
print(radioInfo)
flexRadio = Radio(radioInfo, smartlink)

if __name__ == "__main__":
    main()
