from flask import Flask, request, render_template, redirect, url_for
import os

from SubscriptionManager.py import SubscriptionManager
from TextResponder.py import TextResponder
from MessageParser.py import MessageParser
from types.py import MessageType, UnsubscribeMsg, InstructionMsg, SubOpMsg, OpType

messageParser = MessageParser()
subscriptionManager = SubscriptionManager()
textResponder = TextResponder()

# Flask is used as an endpoint for requests
app = Flask(__name__)

@app.route('/addUser', methods=['POST'])
def serveRequests():
	body = request.form['Body'].strip().lower()
	number = request.form['From']
	print("Body: ", body, "Number: ", number)

	msg = messageParser.parse(body)
	if (isinstance(msg, SubOpMsg)):
		if (msg.opType == OpType.QUERY):
			textResponder.sendMenuForServery(number, msg.servery)

		elif (msg.opType == OpType.ADD):
			subscriptionManager.addToServery(number, msg.servery, msg.meal)

		elif (msg.opType == OpType.REMOVE):
			subscriptionManager.removeFromServery(number, msg.servery, msg.meal)

	elif (isinstance(msg, UnsubscribeMsg)):
		subscriptionManager.unsubscribeFromService(number)
		textResponder.sendUnsubscribeConfirmation(number)

	elif (isinstance(msg, InstructionMsg)):
		textResponder.sendInstructions(number)

	else:
		pass

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

# app.run()
