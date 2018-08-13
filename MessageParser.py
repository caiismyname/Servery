from CustomTypes import SubOpMsg, InstructionMsg, UnsubscribeMsg, OpType, Meal, Serveries

from fuzzywuzzy import fuzz, process

class MessageParser:
    def __init__(self):
        serveries = ["north", "south", "west", "baker", "seibel", "sid", "richardson", "rich", "sid richardson", "sid rich", "sidrich"]
        colleges = ["weiss", "hanszen", "will rice", "wrc", "lovett", "duncan", "mcmurtry", "brown", "jones", "martel"]
        self.allOptions = serveries + colleges
        return

    def parse(self, message):
        if self.__containsServeryName(message):
            opType = self.__whichOpType(message)
            meal = self.__whichMeal(message)
            servery = self.__whichServery(message)
            
            return SubOpMsg(opType, meal, servery)

        elif self.__isInstructionsRequest(message):
            return InstructionMsg()
            
        elif self.__isUnsubscribeRequest(message):
            return UnsubscribeMsg()

        return None

    def __containsServeryName(self, message):
        choice, confidence = process.extractOne(message, self.allOptions)
        if confidence >= 80 or (choice == "seibel" and confidence >= 65):
            return True
        else:
            return False

    def __isInstructionsRequest(self, message):
        helpCommands = ["help", "instructions", "what do", "how", "ayuda"]
        if process.extractOne(message, helpCommands)[1] >= 80:
            return True
        else:
            return False

    def __isUnsubscribeRequest(self, message):
        unsubscribeCommands = ["unsubscribe", "leave", "stop", "go away", "fuck you", "end"]
        if process.extractOne(message, unsubscribeCommands)[1] >= 80:
            return True
        else:
            return False

    def __whichOpType(self, message):
        opTypes = ["add", "remove", "delete", "join", "follow"]
        op, confidence = process.extractOne(message, opTypes)
        if confidence < 70:
            return OpType.QUERY
        elif op == "add" or op == "join" or op == "follow":
            return OpType.ADD
        else:
            return OpType.REMOVE

    def __whichMeal(self, message):
        meals = ["lunch", "dinner", "cena", "almuerzo"]
        op, confidence = process.extractOne(message, meals)

        if confidence < 70:
            return Meal.ALL

        if op == "lunch" or op == "almuerzo":
            return Meal.LUNCH
        else:
            return Meal.DINNER

    def __whichServery(self, message):
        choice, confidence = process.extractOne(message, self.allOptions)

        if choice == "west" or choice == "mcmurtry" or choice == "duncan":
            return Serveries.WEST
        elif choice == "south" or choice == "hanszen" or choice == "weiss":
            return Serveries.SOUTH
        elif choice == "north" or choice == "brown" or choice == "martel" or choice == "jones":
            return Serveries.NORTH            
        elif choice == "seibel" or choice == "lovett" or choice == "will rice" or choice == "wrc":
            return Serveries.SEIBEL
        elif choice == "baker":
            return Serveries.BAKER
        elif choice == "sid" or choice == "rich" or choice == "richardson" or choice == "sid richardson" or choice == "sid rich" or choice == "sidrich":
            return Serveries.SID


        

def OLD_parseServeryName(input):
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
