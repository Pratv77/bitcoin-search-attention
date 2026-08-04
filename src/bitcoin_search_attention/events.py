"""Objective Bitcoin price-surge event identification."""

from datetime import timedelta

import pandas as pd

REQUIRED_PRICE_COLUMNS = {"week", "price_usd"}


def validate_weekly_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Return a sorted, validated copy of a weekly Bitcoin price table."""
    missing = REQUIRED_PRICE_COLUMNS.difference(prices.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = prices.loc[:, ["week", "price_usd"]].copy()
    result["week"] = pd.to_datetime(result["week"], utc=True)
    result["price_usd"] = pd.to_numeric(result["price_usd"], errors="raise")
    result = result.sort_values("week", ignore_index=True)

    if result["week"].duplicated().any():
        raise ValueError("Weekly price dates must be unique")
    if result[["week", "price_usd"]].isna().any().any():
        raise ValueError("Weekly price data cannot contain missing values")
    if (result["price_usd"] <= 0).any():
        raise ValueError("Prices must be positive")

    week_steps = result["week"].diff().dropna()
    if not week_steps.eq(timedelta(weeks=1)).all():
        raise ValueError("Weekly price dates must be consecutive seven-day steps")

    return result


def identify_events(
    prices: pd.DataFrame,
    *,
    threshold: float,
    trailing_weeks: int,
    merge_window_weeks: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Identify retained triggers and all threshold crossings.

    A crossing requires the rise ratio to move from below the threshold to at
    least the threshold. Crossings in the trigger week through the following
    ``merge_window_weeks - 1`` weeks are assigned to the retained event.
    """
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if trailing_weeks < 1:
        raise ValueError("trailing_weeks must be at least 1")
    if merge_window_weeks < 1:
        raise ValueError("merge_window_weeks must be at least 1")

    frame = validate_weekly_prices(prices)
    frame["trailing_low"] = (
        frame["price_usd"]
        .shift(1)
        .rolling(window=trailing_weeks, min_periods=trailing_weeks)
        .min()
    )
    frame["rise_from_trailing_low"] = frame["price_usd"] / frame["trailing_low"] - 1
    frame["at_or_above_threshold"] = frame["rise_from_trailing_low"].ge(threshold)
    prior_threshold_state_observed = frame["rise_from_trailing_low"].shift(1).notna()
    frame["is_crossing"] = (
        prior_threshold_state_observed
        & frame["at_or_above_threshold"]
        & ~frame["at_or_above_threshold"].shift(1, fill_value=False)
    )

    crossings = frame.loc[
        frame["is_crossing"],
        ["week", "price_usd", "trailing_low", "rise_from_trailing_low"],
    ].copy()
    crossings["event_id"] = pd.Series(dtype="Int64")
    crossings["retained_trigger"] = False

    event_id = 0
    active_until: pd.Timestamp | None = None
    for row_index, crossing in crossings.iterrows():
        crossing_week = crossing["week"]
        if active_until is None or crossing_week > active_until:
            event_id += 1
            active_until = crossing_week + timedelta(weeks=merge_window_weeks - 1)
            crossings.at[row_index, "retained_trigger"] = True
        crossings.at[row_index, "event_id"] = event_id

    crossings["event_id"] = crossings["event_id"].astype("Int64")
    events = crossings.loc[crossings["retained_trigger"]].copy().reset_index(drop=True)
    events["event_id"] = range(1, len(events) + 1)
    events = events.rename(columns={"week": "trigger_week"})

    return events, crossings.reset_index(drop=True)
