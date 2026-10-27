"""Tests for the Streamlit app's displayed chart."""

from pathlib import Path

import pyarrow.ipc as ipc
import pytest
from streamlit.testing.v1 import AppTest


# Class example supplied by the user: long call, K = 405, premium = 17.65,
# and stock price at expiration = 425; payoff = 20 and profit = 2.35 per share.
def test_short_call_chart_displays_signed_payoff_and_profit():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.radio[1].set_value("Short (write)").run()

    chart = app.get("vega_lite_chart")[0]
    data = ipc.open_stream(chart.proto.datasets[0].data.data).read_all().to_pandas()
    at_425 = data[data["Stock price at expiration (USD)"] == 425].set_index("Measure")

    assert at_425.loc["Payoff", "USD per share"] == pytest.approx(-20.0, abs=1e-12)
    assert at_425.loc["Profit", "USD per share"] == pytest.approx(-2.35, abs=1e-12)
