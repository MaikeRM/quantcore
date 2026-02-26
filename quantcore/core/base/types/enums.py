from enum import Enum, auto

class OptionType(Enum):
    CALL = "Call"
    PUT = "Put"

class DayCountConvention(Enum):
    ACTUAL_360 = "Actual/360"
    ACTUAL_365 = "Actual/365"
    THIRTY_360 = "30/360"
    BUS_252 = "Bus/252"

class Compounding(Enum):
    SIMPLE = auto()
    COMPOUNDED = auto()
    CONTINUOUS = auto()
    SIMPLE_THEN_COMPOUNDED = auto()

class Frequency(Enum):
    NO_FREQUENCY = 0
    ONCE = 1
    ANNUAL = 1
    SEMIANNUAL = 2
    EVERY_FOURTH_MONTH = 3
    QUARTERLY = 4
    BIMONTHLY = 6
    MONTHLY = 12
    EVERY_FOURTH_WEEK = 13
    BIWEEKLY = 26
    WEEKLY = 52
    DAILY = 365
