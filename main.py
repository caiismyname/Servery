import urllib3
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request
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

# Defining Flask here b/c it's only used as an endpoint for Twilio requests
# And apprently this is the syntax for defining handlers.
app = Flask(__name__)

@app.route('/addUser', methods=['POST'])
def addUser():

	print("adding user")

	servery = request.form['Body']
	number = request.form['From']

	print("servery: ", servery, "number: ", number)

	if 'w' in servery:
		servery = "West"
	elif 'bel' in servery:
		servery = "Seibel"
	elif 'n' in servery:
		servery = "North"
	elif 'k' in servery:
		servery = "Baker"
	elif 'ri' in servery:
		servery = "SidRich"
	elif 'ou' in servery:
		servery = "South"
	else:
		return False

	serveryRef = db.reference("serveries/" + servery)
	serveryRef.push({number: number})

	usersRef = db.reference("users")
	usersRef.push({number: servery})

	print("added user to firebase")

	resp = MessagingResponse("You'll received the menu for {} servery".format(servery))

	# r = requests.put("https://servery-cef7b.firebaseio.com/serveries/" + servery + ".json", data='{"+1' + str(number) + '":"+1' + str(number) + '"}') # Data confroms to {"key":"value"}, as a string
	# r2 = requests.put("https://servery-cef7b.firebaseio.com/users.json", data='{"+1' + str(number) + '":"' + servery + '"}')

	# print(r, r2)

	return str(resp), 200

def getUsersOfServery(servery):

	# r = requests.get("https://servery-cef7b.firebaseio.com/serveries/" + servery + ".json")
	# users = json.loads(r.text).keys()
	# print(users)

	ref = db.reference("serveries/" + servery)
	print(ref.get().keys())
	return ref.get().keys()

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


# update()

initEnviron()
# port = int(os.environ.get('PORT', 33507))
# app.run(debug=True, port=port)




