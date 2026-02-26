from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Union, List

class BaseDataSource(ABC):
    """Abstract interface for all market data providers."""
    
    @abstractmethod
    def fetch_history(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """Fetch historical price mapping."""
        pass
        
    @abstractmethod
    def fetch_quotes(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        """Fetch latest quotes for the given tickers."""
        pass
