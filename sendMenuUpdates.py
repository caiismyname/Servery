import os
import sys
from datetime import date, datetime
from dateutil import tz
from dotenv import load_dotenv, find_dotenv

from AdManager import AdManager

import requests
import firebase_admin
from firebase_admin import credentials, db
import plivo

serveries = ["Seibel", "North", "Baker", "SidRich", "South", "West"]
northServeries = ["North", "West"]
southServeries = ["Seibel", "SidRich", "South", "Baker"]
northWeekendServery = "North"
southWeekendServery = "Seibel"

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
initFirebase()
adManager = AdManager(db)
testMode = False

################
# Plivo
################

def sendBulkMessage(recipients, message):
	delimitedRecipients = "<".join(str(r) for r in recipients)
	if not testMode:
		client = plivo.RestClient()
		response = client.messages.create(
			src=plivoPhoneNumber,
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

# For use on weekends, to send only one menu instead of 
# the subscribed serveries
def splitUsersNorthSouth(meal):
	allUsers = db.reference("users").get()
	northUsers = []
	southUsers = []

	for user in allUsers:
		for servery in northServeries:
			if servery in allUsers[user][meal]:
				northUsers.append(user)
				break
		
		for servery in southServeries:
			if servery in allUsers[user][meal]:
				southUsers.append(user)
				break
	
	return {"north": northUsers, "south": southUsers}

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

# Returns "lunch" or "dinner"
def getMeal():
	fromZone = tz.gettz('UTC')
	toZone = tz.gettz('America/Chicago')
	utc = datetime.utcnow().replace(tzinfo=fromZone)
	houstonTime = utc.astimezone(toZone)

	if houstonTime.hour <= 13:
		return "lunch"
	elif houstonTime.hour > 13:
		return "dinner"

######################
# Put it all together
######################

def updateUsers():
	weekdays = [1,2,3,4,5]
	today = date.today()
	isWeekday = today.isoweekday() in weekdays
	meal = getMeal()
	menus = db.reference("menus").get()
	ad = adManager.getMenuUpdateAd()

	# On weekdays, go through serveries and send menus for everyone subscribed to a servery
	if isWeekday:
		for servery in serveries:
			message = "{} {}".format(menus[servery], ad)
			users = getUsersOfServery(servery, meal)
			splitAndSend(users, message)
	# On weekends, iterate through users and send menu for North if subscribed to 
	# a north servery, Seibel if south
	else:
		northSouthSplit = splitUsersNorthSouth(meal)
		splitAndSend(northSouthSplit["north"], "{} {}".format(menus["North"], ad))
		splitAndSend(northSouthSplit["south"], "{} {}".format(menus["Seibel"], ad))



if (len(sys.argv) > 1):
	if ("-t" in sys.argv):
		testMode = True

# if (os.environ.get("NOT-HEROKU") == "TRUE"):
# 	testMode = True

updateUsers()