import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv, find_dotenv
import os
import datetime
import time


serveries = ["Seibel", "North", "Baker", "South", "West", "SidRich"]

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


def initEnviron():
	load_dotenv(find_dotenv())
	initFirebase()

def countAllUsers():
	ref = db.reference("users/")
	return len(ref.get().keys())

def countUsersPerServery(servery):
	ref = db.reference("serveries/" + servery)
	return len(ref.get().keys())


def saveStats():
	stats = {}
	stats['total'] = countAllUsers()

	for servery in serveries:
		stats[servery] = countUsersPerServery(servery)

	now = datetime.datetime.now()
	date = str(now.year) + "-" + str(now.month) + "-" + str(now.day)

	timeModifier = time.strftime("%p")

	print("Logging daily stats for: " + date + "-" + timeModifier)
	print(stats)

	ref = db.reference("statistics/" + date + "/" + timeModifier)
	ref.set(stats)

initEnviron()

saveStats()