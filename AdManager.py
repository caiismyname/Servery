from datetime import date, datetime
from dateutil import tz

from firebase_admin import db

class AdManager:
    def __init__(self, db):
        self.db = db

    def __getMeal(self):
        fromZone = tz.gettz('UTC')
        toZone = tz.gettz('America/Chicago')
        utc = datetime.utcnow().replace(tzinfo=fromZone)
        houstonTime = utc.astimezone(toZone)

        if houstonTime.hour <= 13:
            return "lunch"
        elif houstonTime.hour > 13:
            return "dinner"

    # Returns the ad corresponding to the upcoming meal + day.
    # Is used for the large-audience lunch and dinner updates (aka "menu update")
    def getMenuUpdateAd(self):
        dayOfWeek = date.today().isoweekday()
        meal = self.__getMeal()

        adMessage = self.db.reference("ads/menuUpdate/{}/{}".format(dayOfWeek, meal)).get()
        print("MenuUpdate ad: [{}] for {}:{}".format(adMessage, dayOfWeek, meal))
        if adMessage == "None":
            return ""
        return adMessage

