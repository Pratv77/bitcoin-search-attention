import pandas as pd
import pytest

from bitcoin_search_attention.events import identify_events, validate_weekly_prices


def weekly_prices(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "week": pd.date_range(
                "2020-01-05", periods=len(values), freq="W-SUN", tz="UTC"
            ),
            "price_usd": values,
        }
    )


def test_trigger_requires_crossing_from_below() -> None:
    prices = weekly_prices([10, 10, 10, 19, 20, 21, 22, 23, 24])

    events, crossings = identify_events(
        prices, threshold=1.0, trailing_weeks=3, merge_window_weeks=2
    )

    assert len(events) == 1
    assert len(crossings) == 1
    assert events.loc[0, "trigger_week"] == prices.loc[4, "week"]


def test_first_computable_threshold_state_is_not_a_crossing() -> None:
    prices = weekly_prices([10, 10, 10, 20, 21, 22])

    events, crossings = identify_events(
        prices, threshold=1.0, trailing_weeks=3, merge_window_weeks=2
    )

    assert events.empty
    assert crossings.empty


def test_nearby_recrossing_is_merged() -> None:
    prices = weekly_prices([10, 10, 10, 19, 20, 10, 20])

    events, crossings = identify_events(
        prices, threshold=1.0, trailing_weeks=3, merge_window_weeks=5
    )

    assert len(crossings) == 2
    assert len(events) == 1
    assert crossings["event_id"].tolist() == [1, 1]


def test_crossing_after_merge_window_starts_new_event() -> None:
    prices = weekly_prices([10, 10, 10, 19, 20, 10, 15, 15, 10, 20])

    events, crossings = identify_events(
        prices, threshold=1.0, trailing_weeks=3, merge_window_weeks=4
    )

    assert len(crossings) == 2
    assert len(events) == 2
    assert crossings["event_id"].tolist() == [1, 2]


def test_duplicate_weeks_are_rejected() -> None:
    prices = weekly_prices([10, 11, 12])
    prices.loc[2, "week"] = prices.loc[1, "week"]

    with pytest.raises(ValueError, match="unique"):
        validate_weekly_prices(prices)
