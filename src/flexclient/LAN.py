# import http.client, pdb, socket, ssl, threading, select
import socket, threading
from json import (
    loads,
)  # Only needed if using .loads() instead of manually parsing the final server response


class LANListen(threading.Thread):
    """Thread to listen for radio announcementsdiscovery packets on the LAN"""

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", 4992))  # Radio discovery uses port 4992
        self.running = True

    def run(self):
        # print("\n...Thread started...\n")
        while self.running:
            m = self.socket.recvfrom(1024)
            print(m[0])
        # print("\n...Thread ended...\n")


class LANDiscovery(object):
    """Class which discovers radios on the LAN"""

    def __init__(self):
        self.listenThread = LANListen()
        self.listenThread.start()

    def ParseRadios(self, radioString):
        """retrieve necessary radio info"""
        desirable_txt = {
            "serial": None,
            "public_ip": None,
            "public_upnp_tls_port": None,
            "public_upnp_udp_port": None,
            "upnp_supported": None,
            "public_tls_port": None,
            "public_udp_port": None,
        }
        for ra in radioString.split(" "):
            for txt in desirable_txt.keys():
                if txt in ra:
                    desirable_txt[txt] = ra.split("=")[1]

        return desirable_txt


#    def GetRadioFromAvailable(self, serial_no):
#        for radio in self.radio_list:
#            if radio["serial"] == serial_no:
#                return radio
#        raise ValueError("Requested serial number not in authorized list")
#
#    def CloseLink(self):
#        self.listenThread.running = False
#        self.listenThread.join()  # End thread manually
#        # del self
#        self.wrapped_server_sock.close()
#        self.server_sock.close()
