import os
import sys
from dotenv import load_dotenv, find_dotenv

import firebase_admin
from firebase_admin import credentials, db
import plivo


# Sets up environment variables for secrets
def initFirebase():
	load_dotenv(find_dotenv())

	privateKeySplit = os.environ.get("FIREBASE-PRIVATE-KEY").split("\\n")
	privateKey = ""
	for portion in privateKeySplit:
		privateKey += portion + "\n"

	serviceAccountKey = {
		'type': os.environ.get("FIREBASE-TYPE"),
		# 'project_id': os.environ.get("FIREBASE-PROJECT-ID"), 
		# 'private_key_id': os.environ.get("FIREBASE-PRIVATE-KEY-ID"),
		'private_key': privateKey,
		'client_email': os.environ.get("FIREBASE-CLIENT-EMAIL"), 
		# 'client_id': os.environ.get("FIREBASE-CLIENT-ID"),
		# 'auth_uri': os.environ.get("FIREBASE-AUTH-URI"),
		'token_uri': os.environ.get("FIREBASE-TOKEN-URI"),
		# 'auth_provider_x509_cert_url': os.environ.get("FIREBASE-AUTH-PROVIDER"),
		# 'client_x509_cert_url': os.environ.get("FIREBASE-CLIENT-CERT-URL")
	}

	cred = credentials.Certificate(serviceAccountKey)
	firebase_admin.initialize_app(cred, {"databaseURL": "https://servery-cef7b.firebaseio.com"})

plivoPhoneNumber = "17137144366"
plivoTollFreeNumber = "18552091827"
initFirebase()
testMode = False

################
# Plivo
################

def sendBulkMessage(recipients, message):
	delimitedRecipients = "<".join(str(r) for r in recipients)
	if not testMode:
		client = plivo.RestClient()
		response = client.messages.create(
			src=plivoTollFreeNumber,
			dst=delimitedRecipients,
			text=message)
		print(response)
	print("Sending: [{}] to [{}]".format(message, delimitedRecipients))

################
# Helpers
################

def getUsersOfServery(servery, meal):
	ref = db.reference("serveries/{}/{}".format(servery, meal))
	return ref.get().keys()

def getAllUsers():
    ref = db.reference("users")
    return ref.get().keys()

def splitAndSend(recipients, message):
	groups = []
	counter = 0
	tempList = []
	for r in recipients:
		if r == "foo":
			continue

		tempList.append(r)
		counter += 1

		if counter == 49:
			groups.append(tempList)
			tempList = []
			counter = 0
	
	# Put the last group into the overall group list
	if len(tempList) > 0:
		groups.append(tempList)

	for group in groups:
		sendBulkMessage(group, message)

def broadcastMessage(message):
    splitAndSend(getAllUsers(), message)

if (len(sys.argv) > 1):
    if ("-t" in sys.argv):
        testMode = True
    else:
        broadcastMessage(sys.argv[1])