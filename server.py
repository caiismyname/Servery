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
	resp = MessagingResponse()
	body = request.form['Body']
	number = request.form['From']
	print("Body: ", body, "Number: ", number)

	if body.strip().upper() == "MENU":
		resp.message(getMenu(getServery(number)))
		return str(resp), 200

	if 'we' in body:
		servery = "West"
	elif 'bel' in body:
		servery = "Seibel"
	elif 'no' in body:
		servery = "North"
	elif 'ak' in body:
		servery = "Baker"
	elif 'ri' in body:
		servery = "SidRich"
	elif 'ou' in body:
		servery = "South"
	else:
		resp.message("Sorry, I don't understand. Text \"menu\" for the menu.")
		return str(resp), 200

	serveryRef = db.reference("serveries/" + servery + "/+" + number)
	serveryRef.set(number)

	usersRef = db.reference("users/+" + number)
	usersRef.set(servery)

	print("Added user " + str(number) + " to firebase")

	resp.message("You'll receive the menu for {} servery".format(servery))

	return str(resp), 200

def getUsersOfServery(servery):
	ref = db.reference("serveries/" + servery)
	print(ref.get().keys())
	return ref.get().keys()

def getMenu(servery):
	ref = db.reference("menus/" + servery)
	return ref.get()

def getServery(number):
	ref = db.reference("users/+" + number)
	return ref.get()


################
# Put it all together
################

# Sets up enviornment variables for secrets
def initEnviron():
	load_dotenv(find_dotenv())
	initTwilio()
	initFirebase()


initEnviron()

