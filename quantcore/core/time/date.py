import datetime as dt

class Date:
    """Wrapper around datetime.date providing mathematical offsets."""
    
    def __init__(self, year: int, month: int, day: int):
        self._date = dt.date(year, month, day)

    @classmethod
    def from_datetime(cls, date_obj: dt.date) -> 'Date':
        return cls(date_obj.year, date_obj.month, date_obj.day)

    @property
    def year(self): return self._date.year
    
    @property
    def month(self): return self._date.month
    
    @property
    def day(self): return self._date.day

    def to_datetime(self) -> dt.date:
        return self._date

    def __sub__(self, other: 'Date') -> int:
        return (self._date - other._date).days

    def __add__(self, days: int) -> 'Date':
        new_date = self._date + dt.timedelta(days=days)
        return Date.from_datetime(new_date)

    def __lt__(self, other: 'Date') -> bool:
        return self._date < other._date
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Date):
            return False
        return self._date == other._date
        
    def __hash__(self):
        return hash(self._date)
        
    def __str__(self):
        return self._date.strftime("%Y-%m-%d")

    def __repr__(self):
        return f"Date({self.year}, {self.month}, {self.day})"
