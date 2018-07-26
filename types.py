from enum import Enum

class OpType(Enum):
    ADD = "add"
    REMOVE = "remove"
    QUERY = "query"

class Meal(Enum):
    LUNCH = "lunch"
    DINNER = "dinner"
    ALL = "lunch and dinner"

class Serveries(Enum):
    SID = "SidRich"
    SEIBEL = "Seibel"
    BAKER = "Baker"
    NORTH = "North"
    SOUTH = "South"
    WEST = "West"

class MessageType():
    def __init__(self):
        return

class InstructionMsg(MessageType):
    def __init__self(self):
        super()
        return

class UnsubscribeMsg(MessageType):
    def __init__self(self):
        super()
        return

class QueryMsg(MessageType):
    def __init__self(self, servery):
        super()
        self.servery = servery
        return

class SubOpMsg(MessageType):
    def __init__self(self, opType, meal, servery):
        super()
        self.opType = opType
        self.meal = meal
        self.servery = servery
        return
