import http.client, pdb, socket, ssl, threading, select


def ParseRead(string):
	print(string)
	read_type = string[0]
	if read_type == "R":
		ParseReply(string)
	elif read_type == "S":
		ParseStatus(string)
	elif read_type == "M":
		ParseMessage(string)
	elif read_type == "H":
		ParseHandle(string)
	elif read_type == "V":
		ParseVersion(string)
	else:
		print("Unknown response from radio") 


def ParseReply(string):
	try:
		(response_code, hex_code, msg) = string.split('|')
	except ValueError:
		print("Error - Incomplete reply")
		return

	# if int(hex_code) == 0:  # msg reponse is "OK"
		# Add {reponse_code: msg} to replies_buffer[]


def ParseStatus(string):
	try:
		(radio_handle, msg) = string.split('|')
	except ValueError:
		print("Error - Invalid status message")
		return

	# if radio_handle == s + CLIENT_HANDLE:  # status message for this client i.e you
		# Add msg to statuses_buffer[]


def ParseMessage(string):
	try:
		(MessageNum, msg) = string.split('|')
	except ValueError:
		print("Error - Invalid message")
		return

	# add msg to log


def ParseHandle(string):
	if len(string) >= 8:
		CLIENT_HANDLE = string[1:9]
	else:
		print("Error - Invalid handle returned")


def ParseVersion(string):
	# global CLIENT_HANDLE
	CLIENT_HANDLE = string.split('H')[1].strip()
	print("New Client Handle: " + CLIENT_HANDLE)