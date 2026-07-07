import re
import time
import logging
import functools
from typing import Any, Callable

logger = logging.getLogger(__name__)


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(level)
    if not log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        log.addHandler(handler)
    return log


def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        logger.debug(f"{func.__name__} completed in {elapsed:.3f}ms")
        return result
    return wrapper


def validate_numeric_string(value: str) -> bool:
    if not isinstance(value, str):
        return False
    pattern = r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$"
    return bool(re.match(pattern, value.strip()))


def clamp(value: float, min_val: float, max_val: float) -> float:
    if min_val > max_val:
        raise ValueError("min_val must be less than or equal to max_val")
    return max(min_val, min(max_val, value))


def round_significant(value: float, sig_figs: int) -> float:
    if sig_figs <= 0:
        raise ValueError("Significant figures must be positive")
    if value == 0:
        return 0.0
    import math
    magnitude = math.floor(math.log10(abs(value)))
    factor = 10 ** (sig_figs - 1 - magnitude)
    return round(value * factor) / factor


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    if b == 0:
        return default
    return a / b


def flatten(nested: list) -> list:
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def chunk(lst: list, size: int) -> list[list]:
    if size <= 0:
        raise ValueError("Chunk size must be positive")
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def is_palindrome(s: str) -> bool:
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", s).lower()
    return cleaned == cleaned[::-1]


def count_digits(n: int) -> int:
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    return len(str(abs(n))) if n != 0 else 1


def reverse_string(s: str) -> str:
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]


def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32


def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32) * 5 / 9


def format_number(n: float, decimals: int = 2) -> str:
    if decimals < 0:
        raise ValueError("Decimal places must be non-negative")
    return f"{n:,.{decimals}f}"


def build_response(success: bool, data: Any = None, message: str = "", code: int = 200) -> dict:
    return {
        "success": success,
        "data": data,
        "message": message,
        "code": code,
        "timestamp": time.time()
    }
