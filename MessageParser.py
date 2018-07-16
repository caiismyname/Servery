from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from types.py import SubOp, Meal, Servery

class MessageParser:
    def __init__(self):
        return

    def parse(self, message):
        if (self.__containsServeryName(message)):
            subOp = self.__whichSubOp(message)
            meal = self.__whichMeal(message)
            servery = self.__whichServery(message)

            if (subOp == SubOp.ADD):
                
            elif (subOp == SubOp.REMOVE):

            elif (subOp == SubOp.NONE):

        elif (self.__isInstructionsRequest(message)):
            
        elif (self.__isUnsubscribeRequest(message)):

    def __containsServeryName(self, message):

    def __isInstructionsRequest(self, message):

    def __isUnsubscribeRequest(self, message):

    def __whichSubOp(self, message):

    def __whichMeal(self, message):

    def __whichServery(self, messsage):




def parseServeryName(input):
	input = input.strip().lower() 
	
	if 'west' in input:
		return "West"
	elif 'bel' in input or 'ble' in input:
		return "Seibel"
	elif 'north' in input:
		return "North"
	elif 'baker' in input:
		return "Baker"
	elif 'rich' in input or 'sid' in input:
		return "SidRich"
	elif 'south' in input:
		return "South"
	
	return None
