# tests/test_calculator.py

import pytest

from infra_ai_service.demo import add, divide, multiply, subtract


def test_add():
    assert add(3, 5) == 8
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(10, 5) == 5
    assert subtract(-1, -1) == 0


def test_multiply():
    assert multiply(3, 5) == 15
    assert multiply(-1, 5) == -5


def test_divide():
    assert divide(10, 2) == 5
    assert divide(10, 5) == 2

    with pytest.raises(ValueError):
        divide(10, 0)
