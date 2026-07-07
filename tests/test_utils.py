import pytest
from app.utils import (
    validate_numeric_string,
    clamp,
    round_significant,
    safe_divide,
    flatten,
    chunk,
    is_palindrome,
    count_digits,
    reverse_string,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    format_number,
    build_response,
)


class TestValidateNumericString:
    def test_integer(self):
        assert validate_numeric_string("42") is True

    def test_float(self):
        assert validate_numeric_string("3.14") is True

    def test_negative(self):
        assert validate_numeric_string("-7") is True

    def test_scientific(self):
        assert validate_numeric_string("1.5e10") is True

    def test_alpha(self):
        assert validate_numeric_string("abc") is False

    def test_empty(self):
        assert validate_numeric_string("") is False

    def test_non_string(self):
        assert validate_numeric_string(123) is False


class TestClamp:
    def test_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_below_min(self):
        assert clamp(-1, 0, 10) == 0

    def test_above_max(self):
        assert clamp(15, 0, 10) == 10

    def test_at_boundary(self):
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10

    def test_invalid_range(self):
        with pytest.raises(ValueError):
            clamp(5, 10, 0)


class TestRoundSignificant:
    def test_basic(self):
        assert round_significant(123.456, 4) == pytest.approx(123.5)

    def test_zero(self):
        assert round_significant(0, 3) == 0.0

    def test_single_sig_fig(self):
        assert round_significant(9876, 1) == pytest.approx(10000.0)

    def test_invalid_sig_figs(self):
        with pytest.raises(ValueError):
            round_significant(100, 0)


class TestSafeDivide:
    def test_normal(self):
        assert safe_divide(10, 2) == 5.0

    def test_zero_divisor_default(self):
        assert safe_divide(5, 0) == 0.0

    def test_zero_divisor_custom_default(self):
        assert safe_divide(5, 0, default=-1) == -1


class TestFlatten:
    def test_nested(self):
        assert flatten([1, [2, [3, 4]]]) == [1, 2, 3, 4]

    def test_flat(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]

    def test_empty(self):
        assert flatten([]) == []

    def test_deeply_nested(self):
        assert flatten([[[[1]]]]) == [1]


class TestChunk:
    def test_basic(self):
        assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

    def test_uneven(self):
        assert chunk([1, 2, 3], 2) == [[1, 2], [3]]

    def test_larger_than_list(self):
        assert chunk([1, 2], 5) == [[1, 2]]

    def test_size_zero(self):
        with pytest.raises(ValueError):
            chunk([1, 2], 0)


class TestIsPalindrome:
    def test_simple(self):
        assert is_palindrome("racecar") is True

    def test_with_spaces(self):
        assert is_palindrome("A man a plan a canal Panama") is True

    def test_not_palindrome(self):
        assert is_palindrome("hello") is False

    def test_empty(self):
        assert is_palindrome("") is True


class TestCountDigits:
    def test_single(self):
        assert count_digits(5) == 1

    def test_multi(self):
        assert count_digits(12345) == 5

    def test_zero(self):
        assert count_digits(0) == 1

    def test_negative(self):
        assert count_digits(-999) == 3

    def test_non_int(self):
        with pytest.raises(TypeError):
            count_digits(3.5)


class TestReverseString:
    def test_basic(self):
        assert reverse_string("hello") == "olleh"

    def test_empty(self):
        assert reverse_string("") == ""

    def test_palindrome(self):
        assert reverse_string("racecar") == "racecar"

    def test_non_string(self):
        with pytest.raises(TypeError):
            reverse_string(123)


class TestTemperatureConversion:
    def test_celsius_to_fahrenheit_zero(self):
        assert celsius_to_fahrenheit(0) == pytest.approx(32.0)

    def test_celsius_to_fahrenheit_100(self):
        assert celsius_to_fahrenheit(100) == pytest.approx(212.0)

    def test_fahrenheit_to_celsius_32(self):
        assert fahrenheit_to_celsius(32) == pytest.approx(0.0)

    def test_fahrenheit_to_celsius_212(self):
        assert fahrenheit_to_celsius(212) == pytest.approx(100.0)

    def test_roundtrip(self):
        c = 37.0
        assert fahrenheit_to_celsius(celsius_to_fahrenheit(c)) == pytest.approx(c)


class TestFormatNumber:
    def test_basic(self):
        assert format_number(1234.5) == "1,234.50"

    def test_zero_decimals(self):
        assert format_number(1234, 0) == "1,234"

    def test_negative(self):
        assert format_number(-9999.99, 2) == "-9,999.99"

    def test_invalid_decimals(self):
        with pytest.raises(ValueError):
            format_number(100, -1)


class TestBuildResponse:
    def test_success(self):
        r = build_response(True, data={"x": 1}, message="ok", code=200)
        assert r["success"] is True
        assert r["data"]["x"] == 1
        assert r["message"] == "ok"
        assert r["code"] == 200
        assert "timestamp" in r

    def test_failure(self):
        r = build_response(False, message="error", code=400)
        assert r["success"] is False
        assert r["code"] == 400
