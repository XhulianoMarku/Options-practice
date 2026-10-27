"""Pricing formulas for the app.

Keep this file free of Streamlit code so every function can be tested with pytest.
Units: S and K in index points or dollars, r and sigma as decimals per year
(0.05, not 5), T in years.
"""
from math import erf, exp, log, sqrt
from typing import Literal

OptionType = Literal["call", "put"]
Position = Literal["long", "short"]


def _validate_expiration_inputs(
    option_type: str,
    stock_price: float,
    strike: float,
    option_price: float | None = None,
) -> None:
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")
    if stock_price < 0 or strike <= 0:
        raise ValueError("stock_price must be nonnegative and strike must be positive")
    if option_price is not None and option_price < 0:
        raise ValueError("option_price must be nonnegative")


def payoff_at_expiration(
    option_type: OptionType, stock_price: float, strike: float
) -> float:
    """Return a call or put payoff at expiration, in dollars per share."""
    _validate_expiration_inputs(option_type, stock_price, strike)
    if option_type == "call":
        return max(stock_price - strike, 0.0)
    return max(strike - stock_price, 0.0)


def profit_at_expiration(
    option_type: OptionType,
    position: Position,
    stock_price: float,
    strike: float,
    option_price: float,
) -> float:
    """Return expiration profit in dollars per share, excluding fees and other costs."""
    _validate_expiration_inputs(option_type, stock_price, strike, option_price)
    if position not in ("long", "short"):
        raise ValueError("position must be 'long' or 'short'")
    payoff = payoff_at_expiration(option_type, stock_price, strike)
    if position == "long":
        return payoff - option_price
    return option_price - payoff


def break_even_price(
    option_type: OptionType, strike: float, option_price: float
) -> float:
    """Return the expiration break-even stock price, in dollars per share."""
    _validate_expiration_inputs(option_type, 0.0, strike, option_price)
    if option_type == "call":
        return strike + option_price
    return strike - option_price


def maximum_gain_and_loss(
    option_type: OptionType, position: Position, strike: float, option_price: float
) -> tuple[float | None, float | None]:
    """Return maximum gain and loss magnitudes per share; None means unbounded."""
    _validate_expiration_inputs(option_type, 0.0, strike, option_price)
    if position not in ("long", "short"):
        raise ValueError("position must be 'long' or 'short'")
    if option_type == "call":
        if position == "long":
            return None, option_price
        return option_price, None
    if position == "long":
        return strike - option_price, option_price
    return option_price, strike - option_price


def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function N(x)."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def bs_d1_d2(S: float, K: float, r: float, sigma: float, T: float) -> tuple[float, float]:
    """Black-Scholes-Merton d1 and d2 (no dividends)."""
    if S <= 0 or K <= 0 or sigma <= 0 or T <= 0:
        raise ValueError("S, K, sigma and T must be positive")
    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    return d1, d1 - sigma * sqrt(T)


def bs_call(S: float, K: float, r: float, sigma: float, T: float) -> float:
    """European call price under Black-Scholes-Merton (no dividends)."""
    d1, d2 = bs_d1_d2(S, K, r, sigma, T)
    return S * norm_cdf(d1) - K * exp(-r * T) * norm_cdf(d2)


def bs_put(S: float, K: float, r: float, sigma: float, T: float) -> float:
    """European put price under Black-Scholes-Merton (no dividends)."""
    d1, d2 = bs_d1_d2(S, K, r, sigma, T)
    return K * exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
