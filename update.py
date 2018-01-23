import urllib3
from twilio.rest import Client
import requests
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv, find_dotenv
import os


serveries = ["Seibel", "North", "Baker", "SidRich", "South", "West"]

class Servery:
	def __init__(self, name):
		self.name = name
		self.menuItems = []

	def setHTMLMenu(self, HTMLMenu):
		self.HTMLMenu = HTMLMenu
		self.parseMenuItems(self.HTMLMenu)

	def parseMenuItems(self, menu):
		start = 0
		while True:
			start = menu.find("menu-item\">", start)
			if start == -1: # No more menu items
				break
			currentPosition = start + 11 # +11 to offset the "menu-item"> part
			# Read the menu item, until the closing </div> tag
			entry = menu[currentPosition]
			while menu[currentPosition + 1] != "<":
				currentPosition += 1
				entry += menu[currentPosition]

			self.menuItems.append(entry)
			start = currentPosition

	def getMenuItems(self):
		return self.menuItems

	def __str__(self):
		return str(self.name) + ": " + str(self.menuItems)[1:-1].replace("'", "")

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

	twilioClient.api.account.messages.create(
	    to=recipient,
	    from_=twilioPhoneNumber,
	    body=message)

	print(recipient, message)


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

def storeMenu(servery, menu):
	ref = db.reference("menus/" + servery)
	ref.set(menu)

################
# Web scraping
################

def getWebsite():
	# Pull webpage
	http = urllib3.PoolManager()
	diningSite = str(http.request('GET', "http://dining.rice.edu").data)

	# Get menu portion
	startIndex = diningSite.find('<div id="main">')
	endIndex = diningSite.find("<!--//End Main-->")
	site = diningSite[startIndex:endIndex]

	return site

def getMenusFromSite(site):
	menuMap = {}

	# Find inidividual menus
	for s in serveries:
		servery = Servery(s)

		startIndex = site.find("<div class=\"servery-title\" id=\"" + s)
		endIndex = site.find("<div class=\"servery-title\"", startIndex + 1)
		servery.setHTMLMenu(site[startIndex:endIndex])

		menuMap[s] = servery
		storeMenu(s, str(severy))
		print(servery)

	return menuMap


################
# Put it all together
################

# Sets up enviornment variables for secrets
def initEnviron():
	load_dotenv(find_dotenv())
	initTwilio()
	initFirebase()

def update():
	initEnviron()
	menuMap = getMenusFromSite(getWebsite())

	for servery in serveries:
		if servery == "Seibel":
			menu = menuMap[servery]
			users = getUsersOfServery(servery)

			for user in users:
				sendMessage(user, str(menu))


update()

