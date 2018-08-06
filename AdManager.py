from datetime import date

from firebase_admin import db

class AdManager:
    def __init__(self, db):
        self.db = db

    # Returns the ad corresponding to the upcoming meal + day.
    # Is used for the large-audience lunch and dinner updates (aka "menu update")
    def getMenuUpdateAd(self):
        dayOfWeek = date.today().isoweekday()
        meal = "lunch"

        adMessage = self.db.reference("ads/menuUpdate/{}/{}".format(dayOfWeek, meal)).get()
        print("MenuUpdate ad: [{}] for {}:{}".format(adMessage, dayOfWeek, meal))
        return adMessage

