from enum import Enum

class SubOp(Enum):
    ADD = "add"
    REMOVE = "remove"
    NONE = "none"

class Meal(Enum):
    LUNCH = "lunch"
    DINNER = "dinner"
    ALL = "all"

class Serveries(Enum):
    SID = "SidRich"
    SEIBEL = "Seibel"
    BAKER = "Baker"
    NORTH = "North"
    SOUTH = "South"
    WEST = "West"

