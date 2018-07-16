from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv, find_dotenv
import os

class TextResponder:
	def __init__(self):
        self.twilioPhoneNumber = "+17137144366"
        self.__initTwilio()
        self.resp = MessagingResponse()
        self.__initFirebase()

    def __initTwilio(self):
        self.twilioClient = Client(os.environ.get("TWILIO-ACCOUNT-SID"), os.environ.get("TWILIO-ACCOUNT-TOKEN"))

    def __initFirebase(self):
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

    def sendMenuForServery(self, user, servery):

    def sendInstructions(self, user):

    def sendAddServeryConfirmation(self, user, servery, meal):

    def sendRemoveServeryConfirmation(self, user, servery, meal):    

    def sendUnsubscribeConfirmation(self, user):
