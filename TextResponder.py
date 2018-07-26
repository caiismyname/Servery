from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv, find_dotenv
import os
import json

class TextResponder:
	def __init__(self):
        self.twilioPhoneNumber = "+17137144366"
        self.__initTwilio()
        self.resp = MessagingResponse()
        self.__initFirebase()
        responseJson = open("responses.json", "r")
        self.responses = json.loads(responseJson.read())
        responseJson.close()

    def __initTwilio(self):
        self.twilioClient = Client(os.environ.get("TWILIO-ACCOUNT-SID"), os.environ.get("TWILIO-ACCOUNT-TOKEN"))

    def __initFirebase(self):
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

    def __sendMessage(self, recipient, message):
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

    def __getMenuForServery(self, servery):
        return db.reference("serveries/{}".format(servery)).get()

    def __getServeriesForUser(self, user):
        all = db.reference("users/{}".format(user)).get()
        lunch = all["lunch"].keys()
        dinner = all["dinner"].keys()
        distinctServeries = set(lunch + dinner)
        
        formattedString = ""
        for servery in distinctServeries:
            formattedString += "{}, ".format(servery)
        
        formattedString = formattedString[:-1] # Strip trailing comma
        return formattedString

    def sendMenuForServery(self, user, servery):
        sendMessage(user,self. __getMenuForServery(servery))

    def sendInstructions(self, user):
        sendMessage(user, self.responses["instructions"].format(self.__getServeriesForUser(user)))

    def sendAddServeryConfirmation(self, user, servery, meal):
        sendMessage(user, self.responses["add-servery-confirmation"].format(servery, meal))

    def sendRemoveServeryConfirmation(self, user, servery, meal):
        sendMessage(user, self.responses["add-servery-confirmation"].format(servery, meal))

    def sendUnsubscribeConfirmation(self, user):
        sendMessage(user, self.responses["unsubscribe-confirmation"])

