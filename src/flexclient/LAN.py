# import http.client, pdb, socket, ssl, threading, select
import socket, threading
from .Vita import VitaPacket
from .DataHandler import ValidatePacketCount
from json import (
    dumps
)  # Only needed for debug printing
from .Common import ParseRadio

class LANListen(threading.Thread):
    """Thread to listen for radio announcementsdiscovery packets on the LAN"""

    def __init__(self, radio_list):
        self.radio_list = radio_list
        threading.Thread.__init__(self, daemon=True)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", 4992))  # Radio discovery uses port 4992
        self.running = True

    def run(self):
        # print("\n...Thread started...\n")
        while self.running:
            udpResponse, addr = self.socket.recvfrom(1024)
            vp = VitaPacket(udpResponse)
            Id = int.from_bytes(vp.class_id, byteorder="big") & int(
                "FFFF", 16
            )
            if Id == int("FFFF", 16):
                # DISCOVERY Packet
                #print("address = ", addr[0])
                #print("payload = ", vp.payload)
                radioData = ParseRadio(vp.payload.decode())
                if radioData['ip'] is '':
                    radioData['ip'] = addr[0]
                inlist = False
                for i, val in enumerate(self.radio_list):
                    if val["ip"] == radioData["ip"]:
                        self.radio_list[i] = radioData
                        inlist = True
                if not inlist:
                    self.radio_list.append(radioData)
            else:
                radioData = None

class LANDiscovery(object):
    """Class which discovers radios on the LAN"""

    def __init__(self):
        self.radio_list = []
        self.listenThread = LANListen(self.radio_list)
        self.listenThread.start()

    def GetRadioFromAvailable(self, serial_no):
        for radio in self.radio_list:
            if radio["serial"] == serial_no:
                return radio
        raise ValueError("Requested serial number not in discovered LAN radios")

#    def CloseLink(self):
#        self.listenThread.running = False
#        self.listenThread.join()  # End thread manually
#        # del self
#        self.wrapped_server_sock.close()
#        self.server_sock.close()
