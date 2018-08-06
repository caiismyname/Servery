import os
from dotenv import load_dotenv, find_dotenv

import urllib3
import requests
import firebase_admin
from firebase_admin import credentials, db
from fuzzywuzzy import fuzz, process

serveries = ["Seibel", "North", "Baker", "SidRich", "South", "West"]
foundSpecials = {}

################
# Firebase
################

def initFirebase():
	# This is so stupid.
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

def storeMenu(servery, menu):
	ref = db.reference("menus/" + servery)
	ref.set(menu)

def storeSpecials():
	for special in targetSpecials
		if special in foundSpecials:
			db.reference("specials/{}".format(special)).set(foundSpecials[special])
		else:
			# Must clear out previously found specials
			db.reference("specials/{}".format(special)).set("")
################
# Web scraping
################

def getWebsite():
	# Pull webpage
	http = urllib3.PoolManager()
	diningSite = str(http.request('GET', "http://dining.rice.edu").data)

	# Get menu portion
	startIndex = diningSite.find('<div id="main">')
	endIndex = diningSite.find("<!--//End Main-->")
	site = diningSite[startIndex:endIndex]

	return site

def parseMenuItems(self, menu, servery):
	menuItems = []
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

		menuItems.append(entry)
		compareAndSaveSpecial(entry, servery)
		start = currentPosition

	return menuItems

def stringifyMenu(serveryName, menuItems):
	return str(serveryName) + ": " + str(menuItems)[1:-1].replace("'", "")

def getMenusFromSite(site):
	menuMap = {}

	# Find inidividual menus
	for s in serveries:
		startIndex = site.find("<div class=\"servery-title\" id=\"" + s)
		endIndex = site.find("<div class=\"servery-title\"", startIndex + 1)
		
		menuMap[s] = parseMenu(site[startIndex:endIndex], s)
		print(stringifyMenu(menuMap[s]))

	return menuMap

def compareAndSaveSpecial(foodItem, servery):
	found, confidence = process.extractOne(foodItem, targetSpecials)
	if confidence > 80:
		foundSpecials[found] = servery

######################
# Put it all together
######################

# Sets up enviornment variables for secrets
def initEnviron():
	load_dotenv(find_dotenv())
	initFirebase()

def updateMenus():
	menuMap = getMenusFromSite(getWebsite())

	for servery in serveries:
		storeMenu(servery, stringifyMenu(menuMap[servery]))

	storeSpecials()

initEnviron()
targetSpecials = db.reference("specials").get().keys()
updateMenus()

