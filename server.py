import os
import sys

from Types import SubOpMsg, OpType, UnsubscribeMsg, InstructionMsg
from SubscriptionManager import SubscriptionManager
from TextResponder import TextResponder
from MessageParser import MessageParser

from firebase_admin import credentials, db
import firebase_admin
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, render_template, redirect, url_for

def __initFirebase():
	load_dotenv(find_dotenv())

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

__initFirebase()
messageParser = MessageParser()
subscriptionManager = SubscriptionManager(db)
textResponder = TextResponder(db)

# Flask is used as an endpoint for requests
app = Flask(__name__)

@app.route('/processMessage', methods=['POST'])
def serveRequests():
	body = request.form['Text'].strip().lower()
	number = request.form['From']
	print("Body: ", body, "Number: ", number)

	msg = messageParser.parse(body)
	if isinstance(msg, SubOpMsg):
		if msg.opType == OpType.QUERY:
			# Must distinguish between query and first time messager
			if subscriptionManager.isUserSubscribed(number):
				print("{}: Queried {}".format(number, msg.servery))
				textResponder.sendMenuForServery(number, msg.servery)
			else:
				print("{}: First time user, subscribing to {}".format(number, msg.servery))
				subscriptionManager.addToServery(number, msg.servery, msg.meal)

		elif msg.opType == OpType.ADD:
			print("{}: Added {}".format(number, msg.servery))
			subscriptionManager.addToServery(number, msg.servery, msg.meal)
			textResponder.sendAddServeryConfirmation(number, msg.servery, msg.meal)

		elif msg.opType == OpType.REMOVE:
			print("{}: Removed {}".format(number, msg.servery))
			subscriptionManager.removeFromServery(number, msg.servery, msg.meal)
			textResponder.sendRemoveServeryConfirmation(number, msg.servery, msg.meal)

	elif isinstance(msg, UnsubscribeMsg):
		print("{}: Unsubscribed".format(number))
		subscriptionManager.unsubscribeFromService(number)
		textResponder.sendUnsubscribeConfirmation(number)

	elif isinstance(msg, InstructionMsg):
		print("{}: Instructions".format(number))
		textResponder.sendInstructions(number)

	else:
		pass
	
	return 'DONE'

# Old method
def addUser():
	resp = MessagingResponse()
	body = request.form['Body'].strip().lower()
	number = request.form['From']
	print("Body: ", body, "Number: ", number)

	try:
		serveries = getServeries(number)

		# Unsubscribe
		if body == "stop" or body == "stopall" or body == "unsubscribe" or body == "cancel" or body == "end" or body == "quit":
			print("Unsubscribing " + str(number))
			removeUser(number)
			return '', 200

		# Resubscribe
		if (body == "start" or body == "yes" or body == "unstop") and serveries == None:
			resp.message("What servery would you like to subscribe to?")
			return str(resp), 200
		elif (body == "start" or body == "yes" or body == "unstop") and serveries is not None:
			print("Resubscribing " + str(number))
			resp.message("You're already subscribed to " + serveries + "")
			return str(resp), 200

		# Help
		if (body == "instructions" or body == "commands" or body == "what do" or body == "how"):
			print("Sending help commands.")
			resp.message('You\'re subscribed to {}. Text the name of any servery to see its next menu. Text "add [servery]" to subscribe to another servery, or "remove [servery]" to unsubscribe. Text "stop" to unsubscribe from this service.'.format(getServeries(number)))
			return str(resp), 200

		# New user
		if serveries is None and parseServeryName(body) is not None:
			print("Adding new user " + str(number) + " to " + parseServeryName(body))
			addUserToServery(number, parseServeryName(body))
			resp.message("You'll receive the menu for {} servery an hour before lunch and dinner. Text the name of any servery to see its next menu. Text \"add [servery]\" to subscribe to another servery, or \"remove [servery]\" to unsubcribe.".format(parseServeryName(body)))
			return str(resp), 200

		# Updating servery preference
		# This has to come before asking menu of non-default servery
		# because the cases overlap.

		# Subscribing to another servery
		if len(body.split(" ")) == 2 and body.split(" ")[0] == "add":
			print("Adding new servery for " + str(number) + ": " + parseServeryName(body.split(" ")[1]))
			newServery = parseServeryName(body.split(" ")[1])
			if newServery is not None:
				addUserToServery(number, newServery)
				resp.message("You will now also receive the menu for {} servery".format(newServery))
				return str(resp), 200

		# Removing a servery subscription
		if len(body.split(" ")) == 2 and body.split(" ")[0] == "remove":
			print("Removing servery for " + str(number) + ": " + parseServeryName(body.split(" ")[1]))
			newServery = parseServeryName(body.split(" ")[1])
			if newServery is not None:
				removeUserFromServery(number, newServery)
				resp.message("You will not receive the menu for {} servery anymore".format(newServery))
				return str(resp), 200

		# Asking for menu of servery
		if serveries is not None and parseServeryName(body) is not None:
			print("Sending menu for arbitrary servery")
			resp.message(getMenu(parseServeryName(body)))
			return str(resp), 200
		
		resp.message("Sorry, I don't understand. Text the name of a servery to see its menu.")
		return str(resp), 200
	except twilio.base.exceptions.TwilioRestException:
		print("TwilioRestException occured.")

if len(sys.argv) > 1:
	if "-r" in sys.argv or "-run" in sys.argv:
		# Specifying -r means it's not Heroku, so by default we want to use testMode
		textResponder.setTestMode(True)
		app.run()
