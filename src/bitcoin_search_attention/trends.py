"""Load, validate, and aggregate official Google Trends exports."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class TrendsValidation:
    query_id: str
    row_count: int
    earliest_date: pd.Timestamp
    latest_date: pd.Timestamp
    duplicate_dates: int
    missing_values: int
    minimum_interest: int
    maximum_interest: int


def load_trends_export(
    path: str | Path,
    *,
    query_id: str,
    expected_start: pd.Timestamp,
    expected_end: pd.Timestamp,
) -> tuple[pd.DataFrame, TrendsValidation]:
    """Load one official Explore CSV and enforce its predetermined range."""
    source_path = Path(path)
    first_line = source_path.read_text(encoding="utf-8-sig").splitlines()[0]
    if first_line.strip() != "Category: All categories":
        raise ValueError(f"{query_id}: unexpected category metadata")

    frame = pd.read_csv(source_path, skiprows=2)
    if len(frame.columns) != 2 or frame.columns[0] != "Day":
        raise ValueError(f"{query_id}: unexpected Google Trends columns")
    if not frame.columns[1].startswith("Bitcoin:"):
        raise ValueError(f"{query_id}: export is not the Bitcoin topic")

    frame.columns = ["date", "search_interest"]
    frame["date"] = pd.to_datetime(frame["date"], utc=True)
    frame["search_interest"] = pd.to_numeric(frame["search_interest"], errors="raise")
    frame = frame.sort_values("date", ignore_index=True)

    duplicate_dates = int(frame["date"].duplicated().sum())
    missing_values = int(frame.isna().sum().sum())
    expected_dates = pd.date_range(expected_start, expected_end, freq="D", tz="UTC")
    if duplicate_dates:
        raise ValueError(f"{query_id}: duplicate dates")
    if missing_values:
        raise ValueError(f"{query_id}: missing values")
    if not frame["date"].equals(pd.Series(expected_dates, name="date")):
        raise ValueError(f"{query_id}: daily coverage does not match manifest")
    if not frame["search_interest"].between(0, 100).all():
        raise ValueError(f"{query_id}: interest values fall outside 0–100")

    validation = TrendsValidation(
        query_id=query_id,
        row_count=len(frame),
        earliest_date=frame["date"].min(),
        latest_date=frame["date"].max(),
        duplicate_dates=duplicate_dates,
        missing_values=missing_values,
        minimum_interest=int(frame["search_interest"].min()),
        maximum_interest=int(frame["search_interest"].max()),
    )
    return frame, validation


def to_weekly_interest(daily: pd.DataFrame, *, query_id: str) -> pd.DataFrame:
    """Average daily interest into complete Sunday-ending weeks."""
    frame = daily.copy()
    days_to_sunday = (6 - frame["date"].dt.weekday) % 7
    frame["week"] = frame["date"] + pd.to_timedelta(days_to_sunday, unit="D")
    weekly = (
        frame.groupby("week", as_index=False)
        .agg(
            search_interest=("search_interest", "mean"),
            daily_observations=("date", "size"),
        )
        .sort_values("week", ignore_index=True)
    )
    if len(weekly) != 25:
        raise ValueError(f"{query_id}: expected 25 weekly observations")
    if not weekly["daily_observations"].eq(7).all():
        raise ValueError(f"{query_id}: at least one week is incomplete")
    weekly.insert(0, "query_id", query_id)
    return weekly
