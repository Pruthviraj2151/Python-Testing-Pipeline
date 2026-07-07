import math
import pytest
from app.calculator import Calculator, CalculatorError, DivisionByZeroError, InvalidInputError


@pytest.fixture
def calc():
    return Calculator()


class TestAdd:
    def test_add_positive(self, calc):
        assert calc.add(2, 3) == 5

    def test_add_negative(self, calc):
        assert calc.add(-4, -6) == -10

    def test_add_mixed(self, calc):
        assert calc.add(-5, 10) == 5

    def test_add_zero(self, calc):
        assert calc.add(0, 0) == 0

    def test_add_floats(self, calc):
        assert calc.add(1.5, 2.5) == pytest.approx(4.0)

    def test_add_large_numbers(self, calc):
        assert calc.add(10**9, 10**9) == 2 * 10**9

    def test_add_invalid_string(self, calc):
        with pytest.raises(InvalidInputError):
            calc.add("a", 1)

    def test_add_none(self, calc):
        with pytest.raises(InvalidInputError):
            calc.add(None, 1)

    def test_add_nan(self, calc):
        with pytest.raises(InvalidInputError):
            calc.add(float("nan"), 1)

    def test_add_inf(self, calc):
        with pytest.raises(InvalidInputError):
            calc.add(float("inf"), 1)


class TestSubtract:
    def test_subtract_basic(self, calc):
        assert calc.subtract(10, 4) == 6

    def test_subtract_negative_result(self, calc):
        assert calc.subtract(3, 7) == -4

    def test_subtract_same(self, calc):
        assert calc.subtract(5, 5) == 0

    def test_subtract_floats(self, calc):
        assert calc.subtract(5.5, 2.5) == pytest.approx(3.0)

    def test_subtract_negative_inputs(self, calc):
        assert calc.subtract(-3, -7) == 4

    def test_subtract_invalid(self, calc):
        with pytest.raises(InvalidInputError):
            calc.subtract("x", 2)


class TestMultiply:
    def test_multiply_positive(self, calc):
        assert calc.multiply(6, 7) == 42

    def test_multiply_by_zero(self, calc):
        assert calc.multiply(100, 0) == 0

    def test_multiply_negative(self, calc):
        assert calc.multiply(-3, 4) == -12

    def test_multiply_negatives(self, calc):
        assert calc.multiply(-3, -4) == 12

    def test_multiply_floats(self, calc):
        assert calc.multiply(2.5, 4.0) == pytest.approx(10.0)

    def test_multiply_invalid(self, calc):
        with pytest.raises(InvalidInputError):
            calc.multiply([], 2)


class TestDivide:
    def test_divide_basic(self, calc):
        assert calc.divide(10, 2) == pytest.approx(5.0)

    def test_divide_float_result(self, calc):
        assert calc.divide(7, 2) == pytest.approx(3.5)

    def test_divide_by_zero(self, calc):
        with pytest.raises(DivisionByZeroError):
            calc.divide(5, 0)

    def test_divide_negative(self, calc):
        assert calc.divide(-10, 2) == pytest.approx(-5.0)

    def test_divide_both_negative(self, calc):
        assert calc.divide(-10, -2) == pytest.approx(5.0)

    def test_divide_invalid(self, calc):
        with pytest.raises(InvalidInputError):
            calc.divide("a", 2)


class TestPower:
    def test_power_basic(self, calc):
        assert calc.power(2, 10) == 1024

    def test_power_zero_exp(self, calc):
        assert calc.power(5, 0) == 1

    def test_power_one_base(self, calc):
        assert calc.power(1, 999) == 1

    def test_power_negative_exp(self, calc):
        assert calc.power(2, -1) == pytest.approx(0.5)

    def test_power_float(self, calc):
        assert calc.power(4, 0.5) == pytest.approx(2.0)

    def test_power_invalid(self, calc):
        with pytest.raises(InvalidInputError):
            calc.power("a", 2)


class TestSqrt:
    def test_sqrt_perfect(self, calc):
        assert calc.sqrt(144) == pytest.approx(12.0)

    def test_sqrt_zero(self, calc):
        assert calc.sqrt(0) == pytest.approx(0.0)

    def test_sqrt_float(self, calc):
        assert calc.sqrt(2.0) == pytest.approx(math.sqrt(2))

    def test_sqrt_negative(self, calc):
        with pytest.raises(InvalidInputError):
            calc.sqrt(-1)

    def test_sqrt_invalid(self, calc):
        with pytest.raises(InvalidInputError):
            calc.sqrt("4")


class TestModulo:
    def test_modulo_basic(self, calc):
        assert calc.modulo(10, 3) == 1

    def test_modulo_even(self, calc):
        assert calc.modulo(10, 5) == 0

    def test_modulo_by_zero(self, calc):
        with pytest.raises(DivisionByZeroError):
            calc.modulo(5, 0)

    def test_modulo_invalid(self, calc):
        with pytest.raises(InvalidInputError):
            calc.modulo("a", 3)


class TestLogarithm:
    def test_log_natural(self, calc):
        assert calc.log(math.e) == pytest.approx(1.0)

    def test_log_base10(self, calc):
        assert calc.log10(1000) == pytest.approx(3.0)

    def test_log_base2(self, calc):
        assert calc.log(8, 2) == pytest.approx(3.0)

    def test_log_negative(self, calc):
        with pytest.raises(InvalidInputError):
            calc.log(-1)

    def test_log_zero(self, calc):
        with pytest.raises(InvalidInputError):
            calc.log(0)

    def test_log_invalid_base(self, calc):
        with pytest.raises(InvalidInputError):
            calc.log(10, 1)


class TestTrigonometry:
    def test_sin_zero(self, calc):
        assert calc.sin(0) == pytest.approx(0.0)

    def test_sin_90(self, calc):
        assert calc.sin(90) == pytest.approx(1.0)

    def test_cos_zero(self, calc):
        assert calc.cos(0) == pytest.approx(1.0)

    def test_cos_90(self, calc):
        assert calc.cos(90) == pytest.approx(0.0, abs=1e-9)

    def test_tan_zero(self, calc):
        assert calc.tan(0) == pytest.approx(0.0)

    def test_tan_45(self, calc):
        assert calc.tan(45) == pytest.approx(1.0)

    def test_tan_90_undefined(self, calc):
        with pytest.raises(InvalidInputError):
            calc.tan(90)

    def test_sin_invalid(self, calc):
        with pytest.raises(InvalidInputError):
            calc.sin("x")


class TestFactorial:
    def test_factorial_zero(self, calc):
        assert calc.factorial(0) == 1

    def test_factorial_one(self, calc):
        assert calc.factorial(1) == 1

    def test_factorial_five(self, calc):
        assert calc.factorial(5) == 120

    def test_factorial_negative(self, calc):
        with pytest.raises(InvalidInputError):
            calc.factorial(-1)

    def test_factorial_too_large(self, calc):
        with pytest.raises(InvalidInputError):
            calc.factorial(1001)

    def test_factorial_float(self, calc):
        with pytest.raises(InvalidInputError):
            calc.factorial(3.5)


class TestGCDLCM:
    def test_gcd_basic(self, calc):
        assert calc.gcd(12, 8) == 4

    def test_gcd_coprime(self, calc):
        assert calc.gcd(7, 13) == 1

    def test_gcd_same(self, calc):
        assert calc.gcd(6, 6) == 6

    def test_lcm_basic(self, calc):
        assert calc.lcm(4, 6) == 12

    def test_lcm_with_zero(self, calc):
        assert calc.lcm(0, 5) == 0

    def test_gcd_float(self, calc):
        with pytest.raises(InvalidInputError):
            calc.gcd(3.5, 2)


class TestStatistics:
    def test_mean_basic(self, calc):
        assert calc.mean([1, 2, 3, 4, 5]) == pytest.approx(3.0)

    def test_median_odd(self, calc):
        assert calc.median([1, 3, 5]) == pytest.approx(3.0)

    def test_median_even(self, calc):
        assert calc.median([1, 2, 3, 4]) == pytest.approx(2.5)

    def test_std_dev(self, calc):
        assert calc.std_dev([2, 4, 4, 4, 5, 5, 7, 9]) == pytest.approx(2.138, rel=1e-3)

    def test_variance(self, calc):
        assert calc.variance([2, 4, 6]) == pytest.approx(4.0)

    def test_mean_empty(self, calc):
        with pytest.raises(InvalidInputError):
            calc.mean([])

    def test_std_dev_single(self, calc):
        with pytest.raises(InvalidInputError):
            calc.std_dev([5])


class TestMiscellaneous:
    def test_percentage(self, calc):
        assert calc.percentage(25, 200) == pytest.approx(12.5)

    def test_percentage_zero_total(self, calc):
        with pytest.raises(DivisionByZeroError):
            calc.percentage(10, 0)

    def test_absolute_negative(self, calc):
        assert calc.absolute(-42) == 42

    def test_absolute_positive(self, calc):
        assert calc.absolute(7) == 7

    def test_floor_divide(self, calc):
        assert calc.floor_divide(10, 3) == 3

    def test_floor_divide_by_zero(self, calc):
        with pytest.raises(DivisionByZeroError):
            calc.floor_divide(5, 0)

    def test_is_prime_true(self, calc):
        assert calc.is_prime(17) is True

    def test_is_prime_false(self, calc):
        assert calc.is_prime(15) is False

    def test_is_prime_one(self, calc):
        assert calc.is_prime(1) is False

    def test_is_prime_two(self, calc):
        assert calc.is_prime(2) is True

    def test_is_prime_float(self, calc):
        with pytest.raises(InvalidInputError):
            calc.is_prime(3.5)


class TestHistory:
    def test_history_records(self, calc):
        calc.add(1, 2)
        calc.multiply(3, 4)
        assert len(calc.get_history()) == 2

    def test_history_clear(self, calc):
        calc.add(1, 2)
        calc.clear_history()
        assert len(calc.get_history()) == 0

    def test_history_content(self, calc):
        calc.add(10, 5)
        history = calc.get_history()
        assert history[0]["operation"] == "add"
        assert history[0]["result"] == 15

    def test_history_isolation(self, calc):
        calc.add(1, 2)
        h1 = calc.get_history()
        h1.append({"fake": True})
        assert len(calc.get_history()) == 1
