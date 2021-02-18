# Smartlink uses TLS 1.3

import socket, ssl, threading, http.client
import string, random
import pdb

username = "president@cardiffars.org.uk"
password = "w1RJ7bux9AKZEIg"

HOST_Auth = "https://frtest.auth0.com"
HOST_FLEX = "https://smartlink.flexradio.com"
# IP = "23.102.155.78"
PORT = 443
client_id = "4Y9fEIIsVYyQo5u6jr7yBWc4lV5ugC2m"	# Smartlink ID
redirect_uri = "https://frtest.auth0.com/mobile"
response_type = "token"
scope = "openid%20offline_access%20email%20given_name%20family_name%20picture"
state = ''.join(random.choices(string.ascii_letters, k=16))

auth0_url = "{_host}/authorize?client_id={_client_id}&redirect_uri={_redirect_uri}&response_type={_response_type}&scope={_scope}&state={_state}".format(_host = HOST_Auth, _client_id = client_id, _redirect_uri = redirect_uri, _response_type = response_type, _scope = scope, _state = state)

# hostname = "www.google.com"
context = ssl.create_default_context()

def pingServer(Socket):
	print("hello world")


conn = http.client.HTTPSConnection(HOST_Auth, port=PORT)
print(conn)

code = None # Need to get authorisation code here

""" payload requires "authorization_code" """
payload = "grant_type=authorization_code&client_id={_client_id}&client_secret={_client_secret}&code={_code}&redirect_uri={_redirect_uri}".format(_client_id = username, _client_secret = password, _code = code, _redirect_uri = redirect_uri)
headers = {"content-type": "application/x-www-form-urlencoded"}


conn.request("POST", "", payload, headers) # NOT WORKING as no authorisation code
res = conn.getresponse()
data = res.read()
print(data)

""" Create socket instance """
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.settimeout(100)

""" Establish connection to FLEX's Auth0 server """
# wSock = ssl.wrap_socket(sock)
# wSock.connect((HOST_FLEX,PORT))	
# print(wSock.version())

# while (True):
# 	pingServer(wSock)



""" Split data into id_token = "" and take id_token as new variable """


