import os
import json

from firebase_admin import db
import plivo

class TextResponder:
    def __init__(self, db):
        self.plivoPhoneNumber = "+17137144366"
        self.__initPlivo()

        self.db = db

        responseJson = open("responses.json", "r")
        self.responses = json.loads(responseJson.read())
        responseJson.close()

    def __initPlivo(self):
        self.client = plivo.RestClient()

    def __sendMessage(self, recipient, message):
        if not self.testMode:
            self.client.messages.create(
                src=self.plivoPhoneNumber,
                dst=recipient,
                text=message)
        else:
            print("Sending [{}] to [{}]".format(message, recipient))

    def __getMenuForServery(self, servery):
        return self.db.reference("menus/{}".format(servery.value)).get()

    def __getServeriesForUser(self, user):
        all = self.db.reference("users/{}".format(user)).get()
        lunch = all["lunch"].keys()
        dinner = all["dinner"].keys()
        distinctServeries = set(lunch + dinner)
        
        formattedString = ""
        for servery in distinctServeries:
            formattedString += "{}, ".format(servery.value)
        
        formattedString = formattedString[:-1] # Strip trailing comma
        return formattedString

    def sendMenuForServery(self, user, servery):
        self.__sendMessage(user,self.__getMenuForServery(servery))

    def sendInstructions(self, user):
        self.__sendMessage(user, self.responses["instructions"].format(self.__getServeriesForUser(user)))

    def sendAddServeryConfirmation(self, user, servery, meal):
        self.__sendMessage(user, self.responses["add-servery-confirmation"].format(servery.value, meal))

    def sendRemoveServeryConfirmation(self, user, servery, meal):
        self.__sendMessage(user, self.responses["add-servery-confirmation"].format(servery.value, meal))

    def sendUnsubscribeConfirmation(self, user):
        self.__sendMessage(user, self.responses["unsubscribe-confirmation"])

    def setTestMode(self, testMode):
        self.testMode = testMode