"""Tests check our numbers against values we verified independently.

Replace or extend these with checks for your own formulas: a worked example (textbook,
DerivaGem, a hand calculation, a published figure), the data itself, another method, or an
identity. Name the source in a comment, as below.
"""
from math import exp

import pytest

from pricing import (
    break_even_price,
    bs_call,
    bs_put,
    maximum_gain_and_loss,
    payoff_at_expiration,
    profit_at_expiration,
)

# Hull, Options, Futures, and Other Derivatives (11th ed.), Ch. 15 worked example:
# S0 = 42, K = 40, r = 10%, sigma = 20%, T = 0.5 years -> c = 4.76, p = 0.81
S, K, R, SIGMA, T = 42.0, 40.0, 0.10, 0.20, 0.5


def test_call_matches_hull_example():
    assert bs_call(S, K, R, SIGMA, T) == pytest.approx(4.76, abs=0.005)


def test_put_matches_hull_example():
    assert bs_put(S, K, R, SIGMA, T) == pytest.approx(0.81, abs=0.005)


def test_put_call_parity():
    # c - p = S - K e^(-rT) must hold for European options on a non-dividend stock
    lhs = bs_call(S, K, R, SIGMA, T) - bs_put(S, K, R, SIGMA, T)
    rhs = S - K * exp(-R * T)
    assert lhs == pytest.approx(rhs, abs=1e-9)


def test_rejects_bad_inputs():
    with pytest.raises(ValueError):
        bs_call(S, K, R, -0.2, T)


# Class example supplied by the user: long call, K = 405, premium = 17.65,
# and stock price at expiration = 425; payoff = 20 and profit = 2.35 per share.
def test_long_call_expiration_matches_class_example():
    assert payoff_at_expiration("call", 425.0, 405.0) == pytest.approx(20.0, abs=1e-12)
    assert profit_at_expiration("call", "long", 425.0, 405.0, 17.65) == pytest.approx(
        2.35, abs=1e-12
    )


# Class example supplied by the user: long put, K = 405, premium = 20,
# and stock price at expiration = 380; payoff = 25 and profit = 5 per share.
def test_long_put_expiration_matches_class_example():
    assert payoff_at_expiration("put", 380.0, 405.0) == pytest.approx(25.0, abs=1e-12)
    assert profit_at_expiration("put", "long", 380.0, 405.0, 20.0) == pytest.approx(
        5.0, abs=1e-12
    )


# Expiration payoffs are zero at the money; negative stock prices are not feasible.
def test_expiration_payoff_at_the_money_and_rejects_negative_stock_price():
    assert payoff_at_expiration("call", 405.0, 405.0) == 0.0
    assert payoff_at_expiration("put", 405.0, 405.0) == 0.0
    with pytest.raises(ValueError):
        payoff_at_expiration("put", -1.0, 405.0)


# Expiration profit identity: otherwise identical long and short positions offset.
@pytest.mark.parametrize("option_type", ["call", "put"])
def test_long_and_short_profits_offset(option_type):
    long_profit = profit_at_expiration(option_type, "long", 425.0, 405.0, 17.65)
    short_profit = profit_at_expiration(option_type, "short", 425.0, 405.0, 17.65)
    assert long_profit + short_profit == pytest.approx(0.0, abs=1e-12)


# At break-even, expiration profit is zero for either option type and position.
@pytest.mark.parametrize(
    ("option_type", "position", "expected_break_even"),
    [
        ("call", "long", 422.65),
        ("call", "short", 422.65),
        ("put", "long", 385.0),
        ("put", "short", 385.0),
    ],
)
def test_break_even_price_produces_zero_profit(
    option_type, position, expected_break_even
):
    premium = 17.65 if option_type == "call" else 20.0
    break_even = break_even_price(option_type, 405.0, premium)
    assert break_even == pytest.approx(expected_break_even, abs=1e-12)
    assert profit_at_expiration(
        option_type, position, break_even, 405.0, premium
    ) == pytest.approx(0.0, abs=1e-12)


# Expiration limiting cases for a nonnegative stock price establish the extrema.
def test_long_put_maximum_gain_and_loss():
    assert maximum_gain_and_loss("put", "long", 405.0, 20.0) == (385.0, 20.0)


def test_call_extrema_identify_unbounded_outcome():
    assert maximum_gain_and_loss("call", "long", 405.0, 17.65) == (None, 17.65)
    assert maximum_gain_and_loss("call", "short", 405.0, 17.65) == (17.65, None)
