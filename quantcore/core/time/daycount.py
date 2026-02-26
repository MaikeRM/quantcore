from abc import ABC, abstractmethod
from typing import Optional
from ..date import Date
from ..calendar import Calendar
from ...base.types.enums import DayCountConvention

class DayCounter(ABC):
    """Abstract base class for day count calculators."""

    @abstractmethod
    def day_count(self, start: Date, end: Date) -> int:
        """Returns the number of days between two dates."""
        pass

    @abstractmethod
    def year_fraction(self, start: Date, end: Date) -> float:
        """Returns the fraction of a year between two dates."""
        pass

class Actual365(DayCounter):
    """Actual/365 day count convention."""
    def day_count(self, start: Date, end: Date) -> int:
        return end - start
    
    def year_fraction(self, start: Date, end: Date) -> float:
        return self.day_count(start, end) / 365.0

class Bus252(DayCounter):
    """Business/252 day count convention commonly used in Brazil."""
    
    def __init__(self, calendar: Calendar):
        self.calendar = calendar

    def day_count(self, start: Date, end: Date) -> int:
        return self.calendar.business_days_between(start, end)
        
    def year_fraction(self, start: Date, end: Date) -> float:
        return self.day_count(start, end) / 252.0
