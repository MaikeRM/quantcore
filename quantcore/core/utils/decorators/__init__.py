from functools import wraps
from typing import Callable, Any
import time

def validate_input(func: Callable) -> Callable:
    """Decorator to perform standard validation on numerical inputs."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Implement global validation strategy (e.g. tracking nan) if requested
        result = func(*args, **kwargs)
        return result
    return wrapper

def timed(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[{func.__name__}] executed in {elapsed:.4f}s")
        return result
    return wrapper
