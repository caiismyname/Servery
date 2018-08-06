import os

from Types import Meal

from firebase_admin import db

class SubscriptionManager:
    def __init__(self, db):
        self.db = db
        
    def unsubscribeFromService(self, user):
        if (self.db.reference("users/{}".format(user)).get() is None):
            self.__removeLatentUser(user)
        else:
            lunchServeries = []
            dinnerServeries = []
            
            lunchRef = self.db.reference("users/{}/lunch".format(user))
            dinnerRef = self.db.reference("users/{}/dinner".format(user))

            if (lunchRef.get() is not None):
                lunchServeries = lunchRef.get().keys()
            if (dinnerRef.get() is not None):
                dinnerServeries = dinnerRef.get().keys()

            for servery in lunchServeries:
                serveryRef = self.db.reference("serveries/{}/lunch/{}}".format(servery, user))
                serveryRef.delete()
            for servery in dinnerServeries:
                serveryRef = self.db.reference("serveries/{}/dinner/{}}".format(servery, user))
                serveryRef.delete()

            userRef = db.reference("users/{}".format(user))
            userRef.delete()
        
    # This method subsribes a user to a servery, but also serves to enter
    # a new user into the system
    def addToServery(self, user, servery, meal):
        # Add to new servery
        if (meal == Meal.LUNCH or meal == Meal.ALL):
            serveryRef = self.db.reference("serveries/{}/lunch/{}".format(servery.value, user))
            serveryRef.set(user)

        if (meal == Meal.DINNER or meal == Meal.ALL):
            serveryRef = self.db.reference("serveries/{}/dinner/{}".format(servery.value, user))
            serveryRef.set(user)

        # Update user entry
        if (meal == Meal.LUNCH or meal == Meal.ALL):
            userRef = self.db.reference("users/{}/lunch/{}/".format(user, servery.value))
            userRef.set(servery)

        if (meal == Meal.DINNER or meal == Meal.ALL):
            userRef = self.db.reference("users/{}/dinner/{}/".format(user, servery.value))
            userRef.set(servery)

        # If it's their first servery after going latent, need to remove from latent list
        self.__removeLatentUser(user)

    def removeFromServery(self, user, servery, meal):
        # Remove from servery
        if (meal == Meal.LUNCH or meal == Meal.ALL):
            serveryRef = self.db.reference("serveries/{}/lunch/{}".format(servery.value, user))
            serveryRef.delete()

        if (meal == Meal.DINNER or meal == Meal.ALL):
            serveryRef = self.db.reference("serveries/{}/dinner/{}".format(servery.value, user))
            serveryRef.delete()

        # Update user entry
        if (meal == Meal.LUNCH or meal == Meal.ALL):
            userRef = self.db.reference("users/{}/lunch/{}/".format(user, servery.value))
            userRef.delete()

        if (meal == Meal.DINNER or meal == Meal.ALL):
            userRef = self.db.reference("users/{}/dinner/{}/".format(user, servery.value))
            userRef.delete()

        # If they're no longer subscribed to any updates, place them in latent mode
        userRef = db.reference("users/{}".format(user))
        if userRef.get() is None:
            self.__createLatentUser(user)

    # Returns if a user is in the database as an existing user.
    # Used to distinguish between first time sign-up messages and query messages
    def isUserSubscribed(self, user):
        return (self.db.reference("users/{}".format(user)).get() is not None)

    def __createLatentUser(self, user):
        userRef = self.db.reference("latentUsers/{}".format(user))
        userRef.set(user)

    def __removeLatentUser(self, user):
        latentRef = self.db.reference("latentUsers/{}".format(user))
        if latentRef.get() is not None:
            latentRef.delete()
