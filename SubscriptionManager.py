import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv, find_dotenv
import os

from types.py import Meal, Servery

class SubscriptionManager:
    def __init__(self):
        self.__initFirebase()
        
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

	def unsubscribeFromService(self, user):
        if (db.reference("users/{}".format(user)).get() is None):
            self.__removeLatentUser(user)
        else:
            lunchServeries = []
            dinnerServeries = []
            
            lunchRef = db.reference("users/{}/lunch".format(user))
            dinnerRef = db.reference("users/{}/dinner".format(user))

            if (lunchRef.get() is not None):
                lunchServeries = lunchRef.get().keys()
            if (dinnerRef.get() is not None):
                dinnerServeries = dinnerRef.get().keys()

            for (servery in lunchServeries):
                serveryRef = db.reference("serveries/{}/lunch/{}}".format(servery, user))
                serveryRef.delete()
            for (servery in dinnerServeries):
                serveryRef = db.reference("serveries/{}/dinner/{}}".format(servery, user))
                serveryRef.delete()

            userRef = db.reference("users/{}".format(user))
            userRef.delete()
        
	def addToServery(self, user, servery, meal):
        # Add to new servery
        if (meal == Meal.LUNCH or meal == Meal.ALL):
            serveryRef = db.reference("serveries/{}/lunch/{}".format(servery, user))
            serverRef.set(user)

        if (meal == Meal.DINNER or meal == Meal.ALL):
            serveryRef = db.reference("serveries/{}/dinner/{}".format(servery, user))
            serverRef.set(user)

        # Update user entry
        if (meal == Meal.LUNCH or meal == Meal.ALL):
            userRef = db.reference("users/{}/lunch/{}/".format(user, servery))
            userRef.set(servery)

        if (meal == Meal.DINNER or meal == Meal.ALL):
            userRef = db.reference("users/{}/dinner/{}/".format(user, servery))
            userRef.set(servery)

        # If it's their first servery after going latent, need to remove from latent list
        self.__removeLatentUser(user)

	def removeFromServery(self, user, servery, meal):
        # Remove from servery
        if (meal == Meal.LUNCH or meal == Meal.ALL):
            serveryRef = db.reference("serveries/{}/lunch/{}".format(servery, user))
            serverRef.delete()

        if (meal == Meal.DINNER or meal == Meal.ALL):
            serveryRef = db.reference("serveries/{}/dinner/{}".format(servery, user))
            serverRef.delete()

        # Update user entry
        if (meal == Meal.LUNCH or meal == Meal.ALL):
            userRef = db.reference("users/{}/lunch/{}/".format(user, servery))
            userRef.delete()

        if (meal == Meal.DINNER or meal == Meal.ALL):
            userRef = db.reference("users/{}/dinner/{}/".format(user, servery))
            userRef.delete()

        # If they're no longer subscribed to any updates, place them in latent mode
        userRef = db.reference("users/{}".format(user))
        if userRef.get() is None:
            self.__createLatentUser(user)

	def __createLatentUser(self, user):
        userRef = db.reference("latentUsers/".format(user))
	    userRef.set(user)

    def __removeLatentUser(self, user):
        latentRef = db.reference("latentUsers/{}".format(user))
        if latentRef.get() is not None:
            latentRef.delete()
