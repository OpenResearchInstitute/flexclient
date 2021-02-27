import http.client, pdb, socket, ssl, threading
from selenium import webdriver  # Needed to instantiate a browser whose current URL may be set and read
from time import sleep          # Needed to prevent busy-waiting for the browser to complete the login process!
from json import loads          # Only needed if using .loads() instead of manually parsing the final server response
from random import choices                  # Used when generating the STATE field
from string import ascii_letters, digits    # Used when generating the STATE field

HOST_FLEX = "smartlink.flexradio.com"
HOST_Auth = "frtest.auth0.com"
REDIRECT_URI = "https://" + HOST_Auth + "/mobile"
CLIENT_ID = "4Y9fEIIsVYyQo5u6jr7yBWc4lV5ugC2m"      # was "C1br1uk8UecHZnUGlIFt1yp62ZNizey3"
SCOPE_LIST = [ 'openid', 'profile' ]
BROWSER = 'chrome'
SERIAL = '1019-9534-6400-6018'


###

def get_response( conn ):
  res = conn.getresponse()
  data = res.read()
  return data.decode( "utf-8" )

###


# Takes a hostname as input, and attempts auth0 authentication using a web browser.
#  The browser is set to Firefox() currently, but can be any which the Selenium module supports (e.g. Chrome()).
#  The output is None for an unsuccessful login, or the response dictionary for a successful one.
#  The token required by smartlink.flexradio.com is stored under the key "id_token".
def get_auth0_tokens( host, client_id, redirect_uri, scope_list, browser = 'chrome' ):
  browsers = { 'firefox' : webdriver.Firefox, 'chrome' : webdriver.Chrome }
  scope = "%20".join( scope_list )
  state_len = 16
  state = "".join( choices( ascii_letters + digits, k = state_len ) )       # was "ypfolheqwpezrxdb" when testing

  conn = http.client.HTTPSConnection( host )
  print(conn)
  # Step 1: request an auth0 code
  #   (this seems to return a redirect to a login URL)
  url1 = "/authorize"
  payload1 = "response_type=code&client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&scope=" + scope + "&state=" + state
  print(url1 + "?" + payload1)
  conn.request( "GET", url1 + "?" + payload1 )
  response = get_response( conn )
  #print( response )
  
  
  # Step 2: open a browser, and display the login URL
  rstr = "Found. Redirecting to "
  if response.find( rstr ) != -1:
    url2 = response.split( rstr )[ 1 ]
    driver = browsers[ browser ](executable_path=r"C:\Program Files\chromedriver_win32\chromedriver.exe")
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
    response = get_response( conn )
    #print( response )
  else:
    print( "ERROR: code was not returned during the login attempt; was your login incorrect?" )
    return
 
 
  # Step 5: attempt to extract the token data (in particular, id_token) from the auth0 server's response
  rstr = '"id_token":"'
  if response.find( rstr ) != -1:
    response = loads( response )
    #print( "id_token is:", response[ "id_token" ] )
    return response
  else:
    print( "ERROR: id_token was not returned by the auth0 server" )
    return


def SendRegisterApplicationMessageToServer(appName, platform, token):
  command = "application register name=" + appName + " platform=" + platform + " token=" + token + '\n'
  radioString = ''
  if wSock.version() != None:
    print(wSock.version())
    wSock.send(command.encode("cp1252"))
    pingThread = threading.Thread(target=PingServer, daemon=True)
    pingThread.start() 
    
    """ Communicate with SmartLink Server """
    
    while True:
      data = wSock.recv(1024).decode("utf-8")
      print(data)
      if len(data) < 1:
        break
      elif ("serial=" + SERIAL) in data:
        radioString = data

    radioData = ParseRadios(radioString)
  else: 
    print("Socket connection not established....")

  return radioData


def ParseRadios(radioList):
  """ retrieve necessary radio info """
  desirable_txt = {"serial": None, "public_ip": None, "public_upnp_tls_port": None, "public_upnp_udp_port": None}
  for ra in radioList.split(' '):
    for txt in desirable_txt.keys():
      if txt in ra:
        desirable_txt[txt] = ra.split('=')[1]

  return desirable_txt


def PingServer():
  while True:
    wSock.send("ping from client".encode())
    sleep(5)


##############
print( "Using browser-based authentication..." )

""" Create socket instance """
context = ssl.create_default_context()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.settimeout(100)

""" Establish connection to FLEX's Auth0 server """
wSock = ssl.wrap_socket(sock)

token_data = get_auth0_tokens( HOST_Auth, CLIENT_ID, REDIRECT_URI, SCOPE_LIST, BROWSER )
# print( "Received id_token =", token_data[ "id_token" ] )

wSock.connect((HOST_FLEX,443))
ChosenRadio = SendRegisterApplicationMessageToServer("FlexModule", "Windows_NT", token_data['id_token'])
print("Radio IP found: " + ChosenRadio['public_ip'])

""" Connect directly with FLEX-6400 """
radio_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
radio_sock.connect((ChosenRadio['public_ip'], int(ChosenRadio['public_upnp_tls_port'])))

radio_sock.send("C1|version".encode("utf-8"))

version_data = radio_sock.recv(2048).decode("utf-8")
print("\n")
print(version_data)

radio_sock.close()


