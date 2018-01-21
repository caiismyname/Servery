import urllib3
from twilio.rest import Client
import requests
import json

serveries = ["Seibel", "North", "Baker", "SidRich", "South", "West"]

class Servery:
	def __init__(self, name):
		self.name = name
		self.menuItems = []

	def setHTMLMenu(self, HTMLMenu):
		self.HTMLMenu = HTMLMenu
		self.parseMenuItems(self.HTMLMenu)

	def parseMenuItems(self, menu):
		start = 0
		while True:
			start = menu.find("menu-item\">", start)
			if start == -1: # No more menu items
				break
			currentPosition = start + 11 # +11 to offset the "menu-item"> part
			# Read the menu item, until the closing </div> tag
			entry = menu[currentPosition]
			while menu[currentPosition + 1] != "<":
				currentPosition += 1
				entry += menu[currentPosition]

			self.menuItems.append(entry)
			start = currentPosition

	def getMenuItems(self):
		return self.menuItems

	def __str__(self):
		return str(self.name) + ": " + str(self.menuItems)[1:-1].replace("'", "")

################
# Twilio
################

twilioAccountSid = "AC1c8c9d1d3d8bff18991ab45434b0e10c"
twilioAccountToken = "ccdcc4c3508ae8665bb91b9739b80676"
twilioPhoneNumber = "+17137144366"

client = Client(twilioAccountSid, twilioAccountToken)

def sendMessage(recipient, message):
	if recipient[:2] != "+1":
		recipient = "+1" + recipient

	client.api.account.messages.create(
	    to=recipient,
	    from_=twilioPhoneNumber,
	    body=message)

	print(recipient, message)


################
# Firebase
################

def addUser(number, servery):

	if 'w' in servery:
		servery = "West"
	elif 'bel' in servery:
		servery = "Seibel"
	elif 'n' in servery:
		servery = "North"
	elif 'k' in servery:
		servery = "Baker"
	elif 'ri' in servery:
		servery = "SidRich"
	elif 'ou' in servery:
		servery = "South"
	else:
		return False


	r = requests.put("https://servery-cef7b.firebaseio.com/serveries/" + servery + ".json", data='{"+1' + str(number) + '":"+1' + str(number) + '"}') # Data confroms to {"key":"value"}, as a string
	r2 = requests.put("https://servery-cef7b.firebaseio.com/users.json", data='{"+1' + str(number) + '":"' + servery + '"}')

	print(r, r2)

def getUsersOfServery(servery):
	r = requests.get("https://servery-cef7b.firebaseio.com/serveries/" + servery + ".json")
	users = json.loads(r.text).keys()

	print(servery, str(users))
	return users

################
# Web scraping
################

def getWebsite():
	# Pull webpage
	http = urllib3.PoolManager()
	diningSite = http.request('GET', "http://dining.rice.edu").data

	# Get menu portion
	startIndex = diningSite.find("<div id=\"main\">")
	endIndex = diningSite.find("<!--//End Main-->")
	site = diningSite[startIndex:endIndex]

	return site

def getMenusFromSite(site):
	menuMap = {}

	# Find inidividual menus
	for s in serveries:
		servery = Servery(s)

		startIndex = site.find("<div class=\"servery-title\" id=\"" + s)
		endIndex = site.find("<div class=\"servery-title\"", startIndex + 1)
		servery.setHTMLMenu(site[startIndex:endIndex])

		menuMap[s] = servery
		print(servery)

	return menuMap


################
# Put it all together
################

def update():
	menuMap = getMenusFromSite(getWebsite())

	for servery in serveries:
		if servery == "Seibel":
			menu = menuMap[servery]
			users = getUsersOfServery(servery)

			for user in users:
				sendMessage(user, str(menu))


update()



