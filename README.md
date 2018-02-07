# Servery

## Product Goals

Messaging bot that sends regular menu updates for lunch/dinner at Rice University. Features include:
- Texts with servery menus an hour before lunch and dinner
- Users can subscribe to multiple serveries, to compare/contrast menus
- Users can send a text with the name of any servery to see the menu for the upcoming meal


## Technical Details
The Servery app source code is written in python. Three seperate files exist. They:
  - Update the menus
  - Send regular update texts to users
  - Handle incoming text messages, including adding new users
  
These are hosted on a free Heroku server, running a simple Flask server via gunicorn.

Text messaging is provided by Twilio, and persistent storage of phone numbers and preferences is handled via Firebase and their firebase-admin Python API.

