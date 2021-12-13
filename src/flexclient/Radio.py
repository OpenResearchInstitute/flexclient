import http.client, pdb, socket, ssl, threading, select
from .Slice import Slice
from .Panafall import Panafall


class Radio(object):
    cmdCnt = 0
    """ Class to create connection with FLEX radio and establish communication channel """

    def __init__(self, radioData, smartlink=None):
        # smartlink is None for local LAN use
        self.ResponseList = {}
        self.StatusList = []
        self.AntList = []
        self.SliceList = [
            Slice(self, 0, "ANT1", "fm")
        ]  # FLEX has a default slice on start up
        self.Panafall = Panafall(
            self, "0x40000000", "0x42000000", 0, 50, 20
        )  # FLEX also has a default Panafall
        self.RxAudioStreamer = None
        if smartlink is not None:
            self.LAN = False
            self.smartlink_sock = (smartlink.wrapped_server_sock)  # socket to comms with Smartlink
        else:
            self.LAN = True
        self.radioData = radioData  # info for the radio about itself
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if smartlink is None:
            self.FLEX_Sock = self.sock
        else:
            self.FLEX_Sock = ssl.wrap_socket(self.sock)  # socket to comms with the FLEX radio
        self.DATA_Sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UdpListening = False

        self.clientHandle = ""
        if not self.LAN:
            self.serverHandle = self.SendConnectMessageToRadio()
        if self.LAN or self.serverHandle:
            if self.LAN:
                hp_port = self.radioData["port"]
            elif self.radioData["upnp_supported"] == "0":
                hp_port = self.radioData["public_tls_port"]
            else:
                hp_port = self.radioData["public_upnp_tls_port"]
            print("ip = ", self.radioData["ip"])
            print("port = ", int(hp_port))
            if self.LAN:
                self.FLEX_Sock.connect((self.radioData["ip"], int(hp_port)))
            else:
                self.FLEX_Sock.connect((self.radioData["public_ip"], int(hp_port)))
                self.WanValidate()
                # print(self.FLEX_Sock.getpeername())
            self.SendCommand("client gui")

    def SendConnectMessageToRadio(self):
        if self.radioData["upnp_supported"] == "0":
            hp_port = self.radioData["public_tls_port"]
        else:
            hp_port = self.radioData["public_upnp_tls_port"]
        if self.radioData["serial"] is None:
            return ""
        command = (
            "application connect serial="
            + self.radioData["serial"]
            + " hole_punch_port="
            + str(hp_port)
            + "\n"
        )
        print("\nSending connect message: " + command)
        self.smartlink_sock.send(command.encode("cp1252"))
        handle_data = self.smartlink_sock.recv(128).decode("cp1252")
        # print(handle_data)
        try:
            handle = handle_data.split("handle=")[1].strip()
            return handle
        except IndexError:
            print("Server Handle not received")
            return ""

    def WanValidate(self):
        command = "wan validate handle=" + self.serverHandle + "\n"
        print("\nSending Wan Validate command: " + command + "\n")
        self.SendCommand(command)

    def OpenUDPConnection(self):
        # tls_command = "client uddport " + self.radioData["public_upnp_udp_port"]
        # self.SendCommand(tls_command)
        if self.radioData["upnp_supported"] == "0":
            udp_port = self.radioData["public_udp_port"]
        else:
            udp_port = self.radioData["public_upnp_udp_port"]
        udp_command = "client udp_register handle=0x" + self.clientHandle
        self.DATA_Sock.sendto(
            udp_command.encode("cp1252"), (self.radioData["public_ip"], int(udp_port))
        )
        self.UdpListening = True
        print("UDP connection opened")

    def CloseUDPConnection(self):
        self.UdpListening = False
        print("UDP connection closed")

    def SendCommand(self, string):
        self.cmdCnt += 1
        self.ResponseList[
            self.cmdCnt
        ] = string  # expecting a response back from the radio regarding this command
        print("C" + str(self.cmdCnt) + "|" + string)
        command = ("C" + str(self.cmdCnt) + "|" + string + "\n").encode("cp1252")
        self.FLEX_Sock.send(command)

    """ Audio Stream Methods """

    def CreateAudioStream(self, isCompressed):
        command = "stream create type=remote_audio_rx compression="
        if isCompressed:
            command += "opus"
        else:
            command += "none"
        self.SendCommand(command)

    # def GetRxAudioStream(self, stream_id):
    # 	return [s for s in self.AudioStreamList if s.stream_id == stream_id][0]

    def RemoveAudioStream(self):
        try:
            command = "stream remove 0x" + self.RxAudioStreamer.stream_id
            self.SendCommand(command)
        except AttributeError:
            # log error
            print("Radio does not have an audio stream to remove!")

    """				"""

    """ Slice Methods """

    def AddSlice(self, freq, ant, mode, streamID=None, source_slice=None):
        # newSlice = Slice(self, freq, ant, mode)
        if freq < 0.03:
            freq = 0.03
            # log attempt to set below min
        elif freq > 54.0:
            freq = 54.0
            # log attempt to set above max

        command = "slice create"
        command += " freq=" + str(freq)
        # if streamID is not None:
        # 	newSlice.slice_id = streamID
        # 	command += (" pan=0x" + str(newSlice.slice_id))
        command += " ant=" + ant
        command += " mode=" + mode
        if source_slice is not None:
            command += " clone_slice=" + str(source_slice)

        # self.SliceList.append(newSlice)
        self.SendCommand(command)

        # add reply expected to reply list = R21|0|0

    def GetSlice(self, s_id):
        return [s for s in self.SliceList if s.slice_id == s_id][0]
        # We want the slice with corresponding id (as this is what FLEX recognises) not list index

    def RemoveSlice(self, slice_id):
        self.GetSlice(slice_id).Remove()
        # Can't remove slice from local list until radio confirms

    def GetSliceList(self):
        self.SendCommand("slice list")

    """ 			"""

    """ Pan Methods """

    def AddPanafall(self, freq, x_pixels=1024, y_pixels=700):
        # need to add antenna variable?
        command = (
            "display panafall create freq="
            + str(freq)
            + " x="
            + str(x_pixels)
            + " y="
            + str(y_pixels)
        )
        self.SendCommand(command)

    def RemovePanafall(self):
        try:
            command = "display panf r " + self.Panafall.panadapter_id
            self.SendCommand(command)
        except AttributeError:
            # log error
            print("Radio does not a have Panafall object to remove!")

    """ 			"""

    def UpdateAntList(self):
        self.SendCommand("ant list")

    def CloseRadio(self):
        # del self
        if not self.LAN:
            self.SendCommand("client disconnect " + self.serverHandle)
        self.FLEX_Sock.close()
        self.sock.close()

    # def __del__(self):
    # 	self.SendCommand("client disconnect " + self.serverHandle)
    # 	self.FLEX_Sock.close()
    # 	self.sock.close()


"""
sub pan all
display panafall create x=1024 y=700
display panafall set 0x40000000 center=1.00 autocenter=0 bandwidth=0.1

sub daxiq all
stream create daxiq=1
dax iq set 1 pan=0x40000000 rate=24000
"""
