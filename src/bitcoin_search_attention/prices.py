from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "event_date",
    "close_price_usd",
    "market_cap_usd",
    "volume_usd",
}


@dataclass(frozen=True)
class PriceValidation:
    row_count: int
    earliest_date: pd.Timestamp
    latest_date: pd.Timestamp
    duplicate_dates: int
    missing_close_prices: int
    nonpositive_close_prices: int
    missing_calendar_dates: tuple[pd.Timestamp, ...]


def load_coingecko_export(path: str | Path) -> tuple[pd.DataFrame, PriceValidation]:
    """Load an untouched CoinGecko CSV and return its validation record."""
    frame = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    frame = frame.loc[:, sorted(REQUIRED_COLUMNS)].copy()
    frame["event_date"] = pd.to_datetime(frame["event_date"], utc=True)
    for column in ("close_price_usd", "market_cap_usd", "volume_usd"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame = frame.sort_values("event_date", ignore_index=True)

    duplicate_dates = int(frame["event_date"].duplicated().sum())
    nonpositive = int(frame["close_price_usd"].dropna().le(0).sum())
    if duplicate_dates:
        raise ValueError("CoinGecko export contains duplicate dates")
    if nonpositive:
        raise ValueError("CoinGecko export contains nonpositive closing prices")

    expected_dates = pd.date_range(
        frame["event_date"].min(), frame["event_date"].max(), freq="D", tz="UTC"
    )
    missing_dates = tuple(expected_dates.difference(frame["event_date"]))
    validation = PriceValidation(
        row_count=len(frame),
        earliest_date=frame["event_date"].min(),
        latest_date=frame["event_date"].max(),
        duplicate_dates=duplicate_dates,
        missing_close_prices=int(frame["close_price_usd"].isna().sum()),
        nonpositive_close_prices=nonpositive,
        missing_calendar_dates=missing_dates,
    )
    return frame, validation


def last_completed_sunday(latest_complete_date: pd.Timestamp) -> pd.Timestamp:
    """Return the latest Sunday on or before a complete daily observation."""
    timestamp = pd.Timestamp(latest_complete_date)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")
    days_since_sunday = (timestamp.weekday() + 1) % 7
    return timestamp.normalize() - timedelta(days=days_since_sunday)


def to_completed_weekly_closes(
    daily: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Convert daily prices to completed Sunday-ending weekly closes."""
    required = {"event_date", "close_price_usd"}
    missing_columns = required.difference(daily.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    usable = daily.loc[:, ["event_date", "close_price_usd"]].dropna().copy()
    usable["event_date"] = pd.to_datetime(usable["event_date"], utc=True)
    usable = usable.sort_values("event_date", ignore_index=True)
    if usable.empty:
        raise ValueError("No complete closing prices are available")

    freeze_week = last_completed_sunday(usable["event_date"].max())
    days_to_sunday = (6 - usable["event_date"].dt.weekday) % 7
    usable["week"] = usable["event_date"] + pd.to_timedelta(days_to_sunday, unit="D")

    weekly = (
        usable.groupby("week", as_index=False)
        .tail(1)
        .rename(columns={"event_date": "source_date", "close_price_usd": "price_usd"})
    )
    weekly = weekly.loc[weekly["week"].le(freeze_week)].copy()
    weekly["source_on_sunday"] = weekly["source_date"].eq(weekly["week"])
    weekly = weekly.loc[
        :, ["week", "price_usd", "source_date", "source_on_sunday"]
    ].reset_index(drop=True)

    expected_weeks = pd.date_range(
        weekly["week"].min(), weekly["week"].max(), freq="W-SUN", tz="UTC"
    )
    if len(expected_weeks.difference(weekly["week"])):
        raise ValueError("Weekly price series contains missing weeks")

    return weekly, freeze_week
