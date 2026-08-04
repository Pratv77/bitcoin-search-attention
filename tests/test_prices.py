import pandas as pd

from bitcoin_search_attention.prices import (
    last_completed_sunday,
    to_completed_weekly_closes,
)


def test_last_completed_sunday_uses_previous_sunday() -> None:
    assert last_completed_sunday(pd.Timestamp("2026-08-03", tz="UTC")) == pd.Timestamp(
        "2026-08-02", tz="UTC"
    )


def test_last_completed_sunday_keeps_sunday() -> None:
    assert last_completed_sunday(pd.Timestamp("2026-08-02", tz="UTC")) == pd.Timestamp(
        "2026-08-02", tz="UTC"
    )


def test_weekly_close_uses_last_available_day_and_drops_partial_week() -> None:
    daily = pd.DataFrame(
        {
            "event_date": pd.to_datetime(
                [
                    "2026-07-26",
                    "2026-07-27",
                    "2026-08-01",
                    "2026-08-02",
                    "2026-08-03",
                ],
                utc=True,
            ),
            "close_price_usd": [10, 11, 12, 13, 14],
        }
    )

    weekly, freeze_week = to_completed_weekly_closes(daily)

    assert freeze_week == pd.Timestamp("2026-08-02", tz="UTC")
    assert weekly["week"].tolist() == [
        pd.Timestamp("2026-07-26", tz="UTC"),
        pd.Timestamp("2026-08-02", tz="UTC"),
    ]
    assert weekly["price_usd"].tolist() == [10, 13]
    assert weekly["source_on_sunday"].tolist() == [True, True]
