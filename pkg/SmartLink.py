import http.client, pdb, socket, ssl, threading, select
from selenium import webdriver  # Needed to instantiate a browser whose current URL may be set and read
from time import sleep          # Needed to prevent busy-waiting for the browser to complete the login process!
from json import loads          # Only needed if using .loads() instead of manually parsing the final server response
from random import choices                  # Used when generating the STATE field
from string import ascii_letters, digits    # Used when generating the STATE field

class PingServer(threading.Thread):
	""" Thread to ping smartlink server whilst user info is inputted """
	def __init__(self, socket):
		threading.Thread.__init__(self, daemon=True)
		self.socket = socket
		self.running = True

	def run(self):
		# print("\n...Thread started...\n")
		while self.running:
			self.socket.send("ping from client\n".encode("cp1252"))
			sleep(5)
		# print("\n...Thread ended...\n")


class SmartLink(object):
	""" Class which connects and authenticates with the SmartLink Server """
	HOST_FLEX = "smartlink.flexradio.com"
	HOST_Auth = "frtest.auth0.com"
	REDIRECT_URI = "https://" + HOST_Auth + "/mobile"
	CLIENT_ID = "4Y9fEIIsVYyQo5u6jr7yBWc4lV5ugC2m"      # was "C1br1uk8UecHZnUGlIFt1yp62ZNizey3"
	SCOPE_LIST = [ 'openid', 'profile' ]
	BROWSER = 'chrome'

	def __init__(self):
		context = ssl.create_default_context()
		self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.wrapped_server_sock = ssl.wrap_socket(self.server_sock)
		self.wrapped_server_sock.connect((self.HOST_FLEX, 443))

		self.pingThread = PingServer(self.wrapped_server_sock)
		self.pingThread.start()


		token_data = self.get_auth0_tokens( self.HOST_Auth, self.CLIENT_ID, self.REDIRECT_URI, self.SCOPE_LIST, self.BROWSER )
		self.radio_list = self.SendRegisterApplicationMessageToServer("FlexModule", "Windows_NT", token_data['id_token'])



	# Takes a hostname as input, and attempts auth0 authentication using a web browser.
	#  The browser is set to Firefox() currently, but can be any which the Selenium module supports (e.g. Chrome()).
	#  The output is None for an unsuccessful login, or the response dictionary for a successful one.
	#  The token required by smartlink.flexradio.com is stored under the key "id_token".
	def get_auth0_tokens(self, host, client_id, redirect_uri, scope_list, browser = 'chrome' ):
		""" to hide non-harmful error """
		options = webdriver.ChromeOptions()
		options.add_experimental_option('excludeSwitches', ['enable-logging'])
		""" """
		browsers = { 'firefox' : webdriver.Firefox, 'chrome' : webdriver.Chrome(options=options, executable_path=r"C:\Program Files\chromedriver_win32\chromedriver.exe") }
		scope = "%20".join( scope_list )
		state_len = 16
		state = "".join( choices( ascii_letters + digits, k = state_len ) )       # was "ypfolheqwpezrxdb" when testing

		conn = http.client.HTTPSConnection( host )
		# print(conn)
		# Step 1: request an auth0 code
		#   (this seems to return a redirect to a login URL)
		url1 = "/authorize"
		payload1 = "response_type=code&client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&scope=" + scope + "&state=" + state
		# print(url1 + "?" + payload1)
		conn.request( "GET", url1 + "?" + payload1 )
		response = self.get_response( conn )
		#print( response )
		
		
		# Step 2: open a browser, and display the login URL
		rstr = "Found. Redirecting to "
		if response.find( rstr ) != -1:
			url2 = response.split( rstr )[ 1 ]
			driver = browsers[ browser ]
			url2 = "https://" + host + url2
			driver.get( url2 )
		else:
			print( "ERROR: request for authorisation did not return a valid login URL" )
			return


		# Step 3: wait for the URL in the browser to change (i.e. the user has entered their login information, hopefully correctly!),
		#   and then close the browser
		response = driver.current_url
		while( response == url2 ):
			sleep( 1 )
			response = driver.current_url
		driver.close()
		
		
		# Step 4: attempt to extract the auth0 code from the URL the browser was directed to,
		#   and use if to request (finally!) the id_token needed to register with smartlink.flexlib.com
		rstr = "code="
		if response.find( rstr ) != -1:
			code = response.split( rstr )[ 1 ]
			url3 = "/frtest.auth0.com/oauth/token"
			headers3 = { 'content-type': "application/x-www-form-urlencoded" }
			payload3 = "response_type=token&client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&scope=" + scope + "&state=" + state + "&grant_type=authorization_code&code=" + code
			conn.request( "POST", url3, payload3, headers3 )
			response = self.get_response( conn )
			#print( response )
		else:
			print( "ERROR: code was not returned during the login attempt; was your login incorrect?" )
			return
	 
	 
	  	# Step 5: attempt to extract the token data (in particular, id_token) from the auth0 server's response
		rstr = '"id_token":"'
		if response.find( rstr ) != -1:
			response = loads( response )
			# print( "id_token is:", response[ "id_token" ] )
			return response
		else:
			print( "ERROR: id_token was not returned by the auth0 server" )
			return


	def get_response(self, conn ):
		res = conn.getresponse()
		data = res.read()
		return data.decode( "utf-8" )


	def SendRegisterApplicationMessageToServer(self, appName, platform, token):
		command = "application register name=" + appName + " platform=" + platform + " token=" + token + '\n'
		radioData = []
		if self.wrapped_server_sock.version() != None:
			# print(self.wrapped_server_sock.version())
			self.wrapped_server_sock.send(command.encode("cp1252"))
			""" Communicate with SmartLink Server """
			inputs = [self.wrapped_server_sock]
			while inputs:
				readable, writable, exceptional = select.select(inputs, [], [], 2)
				# pdb.set_trace()

				for s in readable:
					data = s.recv(1024).decode("utf-8")
					print(data)
					if "radio_name" in data:
						radioData.append(self.ParseRadios(data))
					# else:
					# 	""" Never gets here as no longer any sockets in readable """
					# 	inputs.remove(s)
				if len(readable) < 1:
					""" no sockets are readable so must escape loop """
					inputs.clear()

			"""
			b'radio list radio_name= callsign= serial=1019-9534-6400-6018 model=FLEX-6400 status=Available version=3.1.12.51 inUseIp= inUseHost= last_seen=3/19/2021_12:58:38_PM public_ip=86.6.166.96 public_tls_port=-1 public_udp_port=-1 upnp_supported=1 public_upnp_tls_port=21000 public_upnp_udp_port=22000 max_licensed_version=v3 requires_additional_license=0 radio_license_id=00-1C-2D-05-0E-50 gui_client_programs= gui_client_stations= gui_client_handles= gui_client_ips= gui_client_hosts=|\r\n'
			b'application user_settings callsign=GC0CDF first_name=Cardiff last_name=University\r\n'
			b'application info public_ip=213.1.21.87\r\n'
			THIS IS WHERE A RADIO INSTANCE IS USUALLY CREATED

			"""

		else: 
			print("Socket connection not established....")

		return radioData


	def ParseRadios(self, radioString):
		""" retrieve necessary radio info """
		desirable_txt = {"serial": None, "public_ip": None, "public_upnp_tls_port": None, "public_upnp_udp_port": None}
		for ra in radioString.split(' '):
			for txt in desirable_txt.keys():
				if txt in ra:
					desirable_txt[txt] = ra.split('=')[1]

		return desirable_txt


	def GetRadioFromAvailable(self, serial_no):
		for radio in self.radio_list:
			if radio["serial"] == serial_no:
				return radio
		# Radio not in list
		# Return "not found"


	def CloseLink(self):
		self.pingThread.running = False
		self.pingThread.join() # End thread manually
		self.wrapped_server_sock.close()
		self.server_sock.close()


