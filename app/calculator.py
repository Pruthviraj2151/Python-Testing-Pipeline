import math
import statistics
from typing import Union

Number = Union[int, float]


class CalculatorError(Exception):
    pass


class DivisionByZeroError(CalculatorError):
    pass


class InvalidInputError(CalculatorError):
    pass


class Calculator:
    def __init__(self):
        self.history: list[dict] = []
        self.precision: int = 10

    def _validate(self, *args: Number) -> None:
        for val in args:
            if not isinstance(val, (int, float)):
                raise InvalidInputError(f"Expected numeric value, got {type(val).__name__}")
            if math.isnan(val) or math.isinf(val):
                raise InvalidInputError(f"Value must be finite, got {val}")

    def _record(self, operation: str, result: Number, **kwargs) -> Number:
        entry = {"operation": operation, "result": result, **kwargs}
        self.history.append(entry)
        return result

    def add(self, a: Number, b: Number) -> Number:
        self._validate(a, b)
        return self._record("add", a + b, a=a, b=b)

    def subtract(self, a: Number, b: Number) -> Number:
        self._validate(a, b)
        return self._record("subtract", a - b, a=a, b=b)

    def multiply(self, a: Number, b: Number) -> Number:
        self._validate(a, b)
        return self._record("multiply", a * b, a=a, b=b)

    def divide(self, a: Number, b: Number) -> float:
        self._validate(a, b)
        if b == 0:
            raise DivisionByZeroError("Cannot divide by zero")
        return self._record("divide", a / b, a=a, b=b)

    def power(self, base: Number, exp: Number) -> Number:
        self._validate(base, exp)
        return self._record("power", base ** exp, base=base, exp=exp)

    def sqrt(self, n: Number) -> float:
        self._validate(n)
        if n < 0:
            raise InvalidInputError("Square root of negative number is undefined in real numbers")
        return self._record("sqrt", math.sqrt(n), n=n)

    def modulo(self, a: Number, b: Number) -> Number:
        self._validate(a, b)
        if b == 0:
            raise DivisionByZeroError("Cannot compute modulo with zero divisor")
        return self._record("modulo", a % b, a=a, b=b)

    def absolute(self, n: Number) -> Number:
        self._validate(n)
        return self._record("absolute", abs(n), n=n)

    def floor_divide(self, a: Number, b: Number) -> int:
        self._validate(a, b)
        if b == 0:
            raise DivisionByZeroError("Cannot floor divide by zero")
        return self._record("floor_divide", a // b, a=a, b=b)

    def log(self, n: Number, base: Number = math.e) -> float:
        self._validate(n, base)
        if n <= 0:
            raise InvalidInputError("Logarithm argument must be positive")
        if base <= 0 or base == 1:
            raise InvalidInputError("Logarithm base must be positive and not equal to 1")
        return self._record("log", math.log(n, base), n=n, base=base)

    def log10(self, n: Number) -> float:
        self._validate(n)
        if n <= 0:
            raise InvalidInputError("Logarithm argument must be positive")
        return self._record("log10", math.log10(n), n=n)

    def sin(self, angle_deg: Number) -> float:
        self._validate(angle_deg)
        return self._record("sin", round(math.sin(math.radians(angle_deg)), self.precision), angle=angle_deg)

    def cos(self, angle_deg: Number) -> float:
        self._validate(angle_deg)
        return self._record("cos", round(math.cos(math.radians(angle_deg)), self.precision), angle=angle_deg)

    def tan(self, angle_deg: Number) -> float:
        self._validate(angle_deg)
        if angle_deg % 180 == 90:
            raise InvalidInputError("tan is undefined at 90 + 180n degrees")
        return self._record("tan", round(math.tan(math.radians(angle_deg)), self.precision), angle=angle_deg)

    def factorial(self, n: Number) -> int:
        self._validate(n)
        if not isinstance(n, int) and not n.is_integer():
            raise InvalidInputError("Factorial requires a non-negative integer")
        n = int(n)
        if n < 0:
            raise InvalidInputError("Factorial of negative number is undefined")
        if n > 1000:
            raise InvalidInputError("Input too large for factorial computation")
        return self._record("factorial", math.factorial(n), n=n)

    def gcd(self, a: Number, b: Number) -> int:
        self._validate(a, b)
        if not (isinstance(a, int) and isinstance(b, int)):
            raise InvalidInputError("GCD requires integer inputs")
        return self._record("gcd", math.gcd(abs(a), abs(b)), a=a, b=b)

    def lcm(self, a: Number, b: Number) -> int:
        self._validate(a, b)
        if not (isinstance(a, int) and isinstance(b, int)):
            raise InvalidInputError("LCM requires integer inputs")
        if a == 0 or b == 0:
            return self._record("lcm", 0, a=a, b=b)
        return self._record("lcm", abs(a * b) // math.gcd(abs(a), abs(b)), a=a, b=b)

    def mean(self, data: list) -> float:
        if not data:
            raise InvalidInputError("Cannot compute mean of empty list")
        for val in data:
            self._validate(val)
        return self._record("mean", statistics.mean(data), data=data)

    def median(self, data: list) -> float:
        if not data:
            raise InvalidInputError("Cannot compute median of empty list")
        for val in data:
            self._validate(val)
        return self._record("median", statistics.median(data), data=data)

    def std_dev(self, data: list) -> float:
        if len(data) < 2:
            raise InvalidInputError("Standard deviation requires at least two values")
        for val in data:
            self._validate(val)
        return self._record("std_dev", statistics.stdev(data), data=data)

    def variance(self, data: list) -> float:
        if len(data) < 2:
            raise InvalidInputError("Variance requires at least two values")
        for val in data:
            self._validate(val)
        return self._record("variance", statistics.variance(data), data=data)

    def percentage(self, value: Number, total: Number) -> float:
        self._validate(value, total)
        if total == 0:
            raise DivisionByZeroError("Total cannot be zero for percentage calculation")
        return self._record("percentage", (value / total) * 100, value=value, total=total)

    def is_prime(self, n: Number) -> bool:
        self._validate(n)
        if not isinstance(n, int):
            raise InvalidInputError("Primality check requires an integer")
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True

    def clear_history(self) -> None:
        self.history.clear()

    def get_history(self) -> list[dict]:
        return list(self.history)
