import urllib3
from twilio.rest import Client
import twilio
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv, find_dotenv
import os
from datetime import date

serveries = ["Seibel", "North", "Baker", "SidRich", "South", "West"]
northServeries = ["North", "West"]
southServeries = ["Seibel", "SidRich", "South", "Baker"]
northWeekendServery = "North"
southWeekendServery = "Seibel"

################
# Twilio
################

twilioPhoneNumber = "+17137144366"
twilioClient = None

def initTwilio():
	global twilioClient
	twilioClient = Client(os.environ.get("TWILIO-ACCOUNT-SID"), os.environ.get("TWILIO-ACCOUNT-TOKEN"))

def sendMessage(recipient, message):
	if recipient[:2] != "+1":
		recipient = "+1" + recipient

	try:
		twilioClient.api.account.messages.create(
		    to=recipient,
		    from_=twilioPhoneNumber,
		    body=message)

		print(recipient, message)
	except twilio.base.exceptions.TwilioRestException:
		print("TwilioRestException occured")


################
# Firebase
################

def initFirebase():
	# This is so stupid.
	# Unadultered, the private_key gets ready out with "\\\n" instead of newlines.
	# Putting the key in surrounded by quotes makes it "\n" (literal).
		# Note that the surrounding quotes are only needed on my local machine, not on heroku.
	# Read that, split, then concat actual newlines, to make it a valid private_key.

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

def getUsersOfServery(servery):
	ref = db.reference("serveries/" + servery)
	print(ref.get().keys())
	return ref.get().keys()

def getMenu(servery):
	ref = db.reference("menus/" + servery)
	return ref.get()

def getAllUsers():
	ref = db.reference("users")
	return ref.get()

# 'user' should be a dictionary of the serveries a user is subscribed to
# where the key and value are the same.
def isNorth(user):
	for servery in northServeries:
		if servery in user:
			return True

	return False

# 'user' should be a dictionary of the serveries a user is subscribed to
# where the key and value are the same.
def isSouth(user):
	for servery in southServeries:
		if servery in user:
			return True

	return False

################
# Put it all together
################

# Sets up enviornment variables for secrets
def initEnviron():
	load_dotenv(find_dotenv())
	initTwilio()
	initFirebase()

def updateUsers():
	weekdays = [1,2,3,4,5]
	today = date.today()
	isWeekday = today.isoweekday() in weekdays

	menus = {}
	for servery in serveries:
		menus[servery] = getMenu(servery)

	# On weekdays, go through serveries and send menus for everyone subscribed to a servery
	if isWeekday:
		for servery in serveries:
			menu = menus[servery]
			users = getUsersOfServery(servery)

			for user in users:
				if user != "foo":
					sendMessage(user, str(menu))
	# On weekends, iterate through users and send menu for north if subscribed to 
	# a north servery, seibel if south
	else:
		allUsers = getAllUsers()
		for user in allUsers:
			if isNorth(allUsers[user]):
	 			sendMessage(user, str(menus[northWeekendServery]))

			if isSouth(allUsers[user]):
				sendMessage(user, str(menus[southWeekendServery]))



initEnviron()
updateUsers()

