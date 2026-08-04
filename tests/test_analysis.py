import pandas as pd

from bitcoin_search_attention.analysis import measure_event, results_frame


def test_measure_event_uses_earliest_tie_and_locked_sign_convention() -> None:
    weeks = pd.date_range("2020-01-05", periods=25, freq="W-SUN", tz="UTC")
    prices = pd.DataFrame({"week": weeks, "price_usd": list(range(10, 35))})
    prices.loc[20, "price_usd"] = 100
    prices.loc[21, "price_usd"] = 100
    search_values = [1.0] * 25
    search_values[22] = 50.0
    search_values[23] = 50.0
    search = pd.DataFrame(
        {"query_id": "GT01", "week": weeks, "search_interest": search_values}
    )
    event = pd.Series(
        {
            "analysis": "primary",
            "event_id": "P01",
            "trigger_week": weeks[8],
            "window_start": weeks[0],
            "window_end": weeks[24],
        }
    )

    result = measure_event(
        event, query_id="GT01", weekly_prices=prices, weekly_search=search
    )

    assert result.price_peak_week == weeks[20]
    assert result.search_peak_week == weeks[22]
    assert result.peak_lag_weeks == 2
    assert result.price_tie_count == 2
    assert result.search_tie_count == 2
    assert results_frame([result]).loc[0, "event_id"] == "P01"
