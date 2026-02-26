from typing import Protocol, runtime_checkable

@runtime_checkable
class SupportPricing(Protocol):
    """
    Protocol verifying if an object supports structural pricing mechanisms.
    """
    def is_expired(self) -> bool:
        ...

@runtime_checkable
class SupportGreeks(Protocol):
    """
    Protocol indicating the capability of calculating greek sensitivities.
    """
    def get_greeks(self) -> dict:
        ...
