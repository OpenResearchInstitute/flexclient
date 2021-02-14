import socket, ssl, requests
import pdb

HOST = "https://smartlink.flexradio.com"
IP = "23.102.155.78"
PORT = 443

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(100)

wSock = ssl.wrap_socket(sock)
wSock.connect((IP,PORT))	# using HOST returns a getaddrinfo error


# cert = ssl.get_server_certificate((HOST,PORT))	# Doesn't work yet/ Not sure if right command
# response = requests.get(IP, verify=True)

pdb.set_trace()
