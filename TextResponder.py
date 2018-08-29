import os
import json

from firebase_admin import db
import plivo

class TextResponder:
    def __init__(self, db):
        self.plivoPhoneNumber = "17137144366"
        self.plivoTollFreeNumber = "18552091827"
        self.__initPlivo()
        self.testMode = False
        self.db = db

        responseJson = open("responses.json", "r")
        self.responses = json.loads(responseJson.read())
        responseJson.close()

    def __initPlivo(self):
        self.client = plivo.RestClient()

    def __sendMessage(self, recipient, message):
        if self.testMode == False:
            self.client.messages.create(
                src=self.plivoTollFreeNumber,
                dst=recipient,
                text=message)
        print("Sent [{}] to [{}]".format(message, recipient))

    def __getMenuForServery(self, servery):
        return self.db.reference("menus/{}".format(servery.value)).get()

    def __getServeriesForUser(self, user):
        all = self.db.reference("users/{}".format(user)).get()
        lunch = list(all["lunch"].keys())
        dinner = list(all["dinner"].keys())
        distinctServeries = set(lunch + dinner)
        
        formattedString = ""
        for servery in distinctServeries:
            # Since we're pulling servery names from their string representations
            # in the DB, they're not an enum value here.
            formattedString += "{}, ".format(servery)
        
        formattedString = formattedString[:-2] # Strip trailing comma and space
        return formattedString

    def sendMenuForServery(self, user, servery):
        self.__sendMessage(user,self.__getMenuForServery(servery))

    def sendInstructions(self, user):
        self.__sendMessage(user, self.responses["instructions"].format(self.__getServeriesForUser(user)))

    def sendAddServeryConfirmation(self, user, servery, meal):
        self.__sendMessage(user, self.responses["add-servery-confirmation"].format(servery.value, meal.value))

    def sendRemoveServeryConfirmation(self, user, servery, meal):
        self.__sendMessage(user, self.responses["remove-servery-confirmation"].format(servery.value, meal.value))

    def sendUnsubscribeConfirmation(self, user):
        self.__sendMessage(user, self.responses["unsubscribe-confirmation"])

    def setTestMode(self, testMode):
        self.testMode = testMode