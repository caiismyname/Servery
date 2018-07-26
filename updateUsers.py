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
# Plivo
################

phoneNumber = "+17137144366"

def sendMessage(recipient, message):
	pass

################
# Helpers
################

def getUsersOfServery(servery):
	ref = db.reference("serveries/{}".format(servery))
	print(ref.get().keys())
	return ref.get().keys()

# allUsers should be dict with phone number --> list of serveries mapping
def splitUsersNorthSouth():
	allUsers = db.reference("users").get()
	northUsers = []
	southUsers = []

	for user in allUsers:
		for servery in northServeries:
			if servery in allUsers[user]:
				northUsers.append(user)
				break
		
		for servery in southServeries:
			if servery in allUsers[user]:
				southUsers.append(user)
				break
	
	return {"north": northUsers, "south": southUsers}

def splitInTenAndSend(recipients, message):
	groups = []
	counter = 0
	tempList = []
	for r in recipients:
		if (r == "foo"):
			continue

		tempList.append(r)
		counter += 1

		if (counter == 9):
			groups.append(tempList)
			tempList = []
			counter = 0
	
	# Put the last group into the overall group list
	if (len(tempList) > 0):
		groups.append(tempList)

	for group in groups:
		sendMessage(group, message)

################
# Put it all together
################

# Sets up environment variables for secrets
def initFirebase():
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

def initEnviron():
	load_dotenv(find_dotenv())
	initFirebase()

def updateUsers():
	weekdays = [1,2,3,4,5]
	today = date.today()
	isWeekday = today.isoweekday() in weekdays
	menus = db.reference("menus").get()

	# On weekdays, go through serveries and send menus for everyone subscribed to a servery
	if isWeekday:
		for servery in serveries:
			menu = menus[servery]
			users = getUsersOfServery(servery)
			splitInTenAndSend(users, menu)
	# On weekends, iterate through users and send menu for North if subscribed to 
	# a north servery, Seibel if south
	else:
		northSouthSplit = splitUsersNorthSouth()
		splitInTenAndSend(northSouthSplit["north"], menus["North"])
		splitInTenAndSend(northSouthSplit["south"], menus["Siebel"])



initEnviron()
updateUsers()

