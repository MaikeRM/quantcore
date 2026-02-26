from abc import ABC, abstractmethod
from datetime import date as dt_date
from .date import Date

class Calendar(ABC):
    """Abstract base class for trading calendars."""

    @abstractmethod
    def is_business_day(self, date: Date) -> bool:
        """Return True if the date is a business day."""
        pass

    @abstractmethod
    def is_holiday(self, date: Date) -> bool:
        """Return True if the date is a holiday."""
        pass

    def is_weekend(self, date: Date) -> bool:
        """Return True if the date is a weekend."""
        return date.to_datetime().weekday() >= 5
        
    def is_holiday_or_weekend(self, date: Date) -> bool:
        """Return True if the date is a weekend or holiday."""
        return self.is_weekend(date) or self.is_holiday(date)
    
    def add_business_days(self, date: Date, n: int) -> Date:
        """Adds n business days to a given date."""
        current = date
        step = 1 if n > 0 else -1
        days_added = 0
        target = abs(n)
        
        while days_added < target:
            current = current + step
            if self.is_business_day(current):
                days_added += 1
                
        return current

    def business_days_between(self, start: Date, end: Date) -> int:
        """Returns the number of business days between start (inclusive) and end (exclusive)."""
        if start > end:
            return -self.business_days_between(end, start)
            
        current = start
        count = 0
        while current < end:
            if self.is_business_day(current):
                count += 1
            current = current + 1
            
        return count
