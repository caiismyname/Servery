import urllib2
from twilio.rest import Client

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
		return str(self.name) + ": " + str(self.menuItems)[1:-1]

################
# Twilio
################

twilioAccountSid = "AC1c8c9d1d3d8bff18991ab45434b0e10c"
twilioAccountToken = "ccdcc4c3508ae8665bb91b9739b80676"
twilioPhoneNumber = "+17137144366"

client = Client(twilioAccountSid, twilioAccountToken)

def sendMessage(recipient, message):
	client.api.account.messages.create(
	    to="+1" + recipient,
	    from_=twilioPhoneNumber,
	    body=message)



################
# Web scraping
################

# Pull webpage
diningSite = urllib2.urlopen("http://dining.rice.edu").read()

# Get menu portion
startIndex = diningSite.find("<div id=\"main\">")
endIndex = diningSite.find("<!--//End Main-->")
main = diningSite[startIndex:endIndex]

serveries = ["Seibel", "North", "Baker", "SidRich", "South", "West"]
menuMap = {}

# Find inidividual menus
for s in serveries:
	servery = Servery(s)

	startIndex = main.find("<div class=\"servery-title\" id=\"" + s)
	endIndex = main.find("<div class=\"servery-title\"", startIndex + 1)
	servery.setHTMLMenu(main[startIndex:endIndex])

	menuMap[s] = servery


print menuMap["North"]


