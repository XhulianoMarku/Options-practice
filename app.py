"""Streamlit page for an option position's payoff and profit at expiration."""
import altair as alt
import pandas as pd
import streamlit as st

from pricing import (
    break_even_price,
    maximum_gain_and_loss,
    payoff_at_expiration,
    profit_at_expiration,
)

CONTRACT_MULTIPLIER = 100
OPTION_PRICE = 17.65
CONTRACTS = 1


def _format_amount(amount: float | None) -> str:
    if amount is None:
        return "unlimited"
    return f"USD {amount:,.2f}"


st.set_page_config(page_title="Option payoff at expiration", page_icon="📈")
st.title("Option payoff and profit at expiration")
st.write(
    "Explore how one hypothetical stock option position performs at expiration. "
    "Payoff and profit are shown per share."
)

option_type = st.radio("Option type", ["Call", "Put"], horizontal=True).lower()
position = st.radio("Position", ["Long (buy)", "Short (write)"], horizontal=True)
position_code = "long" if position.startswith("Long") else "short"
strike = st.slider(
    "Strike price (USD)",
    min_value=300,
    max_value=500,
    value=405,
    step=1,
)

st.caption(
    f"Hypothetical assumptions: option price is USD {OPTION_PRICE:.2f} per share; "
    f"contracts: {CONTRACTS}; contract multiplier: {CONTRACT_MULTIPLIER} shares. "
    "Fees and other costs are excluded."
)

break_even = break_even_price(option_type, strike, OPTION_PRICE)
max_gain, max_loss = maximum_gain_and_loss(
    option_type, position_code, strike, OPTION_PRICE
)

st.subheader("At expiration")
st.write(f"**Break-even stock price:** USD {break_even:,.2f}.")
st.write(
    f"**Maximum gain:** {_format_amount(max_gain * CONTRACT_MULTIPLIER * CONTRACTS if max_gain is not None else None)} "
    f"total ({_format_amount(max_gain)} per share)."
)
st.write(
    f"**Maximum loss:** {_format_amount(max_loss * CONTRACT_MULTIPLIER * CONTRACTS if max_loss is not None else None)} "
    f"total ({_format_amount(max_loss)} per share)."
)

stock_prices = range(300, 501)
payoff_sign = 1 if position_code == "long" else -1
chart_data = pd.DataFrame(
    {
        "Stock price at expiration (USD)": list(stock_prices),
        "Payoff": [
            payoff_sign * payoff_at_expiration(option_type, price, strike)
            for price in range(300, 501)
        ],
        "Profit": [
            profit_at_expiration(
                option_type, position_code, price, strike, OPTION_PRICE
            )
            for price in range(300, 501)
        ],
    }
)
chart_data = chart_data.melt(
    id_vars="Stock price at expiration (USD)",
    var_name="Measure",
    value_name="USD per share",
)

chart = (
    alt.Chart(chart_data)
    .mark_line()
    .encode(
        x=alt.X(
            "Stock price at expiration (USD):Q",
            title="Stock price at expiration (USD)",
            scale=alt.Scale(domain=[300, 500]),
        ),
        y=alt.Y("USD per share:Q", title="Payoff / profit (USD per share)"),
        color=alt.Color("Measure:N", title=""),
        tooltip=[
            alt.Tooltip("Stock price at expiration (USD):Q", format=",.2f"),
            alt.Tooltip("Measure:N"),
            alt.Tooltip("USD per share:Q", format=",.2f"),
        ],
    )
    .properties(height=400)
)
st.altair_chart(chart, use_container_width=True)
st.caption(
    "The chart covers expiration stock prices from USD 300 to USD 500. "
    "The break-even value above is shown even if it falls outside this range."
)
