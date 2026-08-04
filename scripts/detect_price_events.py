"""Detect locked price events and create Google Trends collection windows."""

from datetime import timedelta
from pathlib import Path

import pandas as pd

from bitcoin_search_attention.config import CONFIG
from bitcoin_search_attention.events import identify_events

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEEKLY_PATH = PROJECT_ROOT / "data" / "interim" / "bitcoin_weekly_prices.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim"


def eligible_events(events: pd.DataFrame, weekly: pd.DataFrame) -> pd.DataFrame:
    """Attach fixed windows and retain events with complete price coverage."""
    result = events.copy()
    result["window_start"] = result["trigger_week"] - timedelta(
        weeks=CONFIG.pre_trigger_weeks
    )
    result["window_end"] = result["trigger_week"] + timedelta(
        weeks=CONFIG.post_trigger_weeks
    )
    first_week = weekly["week"].min()
    last_week = weekly["week"].max()
    result["price_window_complete"] = result["window_start"].ge(first_week) & result[
        "window_end"
    ].le(last_week)
    return result.loc[result["price_window_complete"]].reset_index(drop=True)


def detect_for_threshold(
    weekly: pd.DataFrame, threshold: float, label: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    events, crossings = identify_events(
        weekly,
        threshold=threshold,
        trailing_weeks=CONFIG.trailing_low_weeks,
        merge_window_weeks=CONFIG.event_window_weeks,
    )
    events = eligible_events(events, weekly)
    events.insert(0, "analysis", label)
    events.insert(1, "threshold", threshold)
    events["event_id"] = [
        f"{label[0].upper()}{value:02d}" for value in range(1, len(events) + 1)
    ]
    crossings.insert(0, "analysis", label)
    crossings.insert(1, "threshold", threshold)
    return events, crossings


def build_trends_windows(
    primary: pd.DataFrame, alternate: pd.DataFrame
) -> pd.DataFrame:
    """Build one collection row per unique event window."""
    combined = pd.concat([primary, alternate], ignore_index=True)
    windows = (
        combined.groupby(["trigger_week", "window_start", "window_end"], as_index=False)
        .agg(
            analyses=("analysis", lambda values: "+".join(sorted(values))),
            event_ids=("event_id", lambda values: "+".join(values)),
        )
        .sort_values("trigger_week", ignore_index=True)
    )
    windows.insert(
        0, "query_id", [f"GT{value:02d}" for value in range(1, len(windows) + 1)]
    )
    windows["query_start"] = windows["window_start"] - timedelta(days=6)
    windows["query_end"] = windows["window_end"]
    return windows


def main() -> None:
    weekly = pd.read_csv(WEEKLY_PATH, parse_dates=["week", "source_date"])
    primary, primary_crossings = detect_for_threshold(
        weekly, CONFIG.primary_threshold, "primary"
    )
    alternate, alternate_crossings = detect_for_threshold(
        weekly, CONFIG.alternate_threshold, "alternate"
    )
    windows = build_trends_windows(primary, alternate)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    primary.to_csv(OUTPUT_DIR / "price_events_primary.csv", index=False)
    alternate.to_csv(OUTPUT_DIR / "price_events_alternate.csv", index=False)
    primary_crossings.to_csv(OUTPUT_DIR / "price_crossings_primary.csv", index=False)
    alternate_crossings.to_csv(
        OUTPUT_DIR / "price_crossings_alternate.csv", index=False
    )
    windows.to_csv(OUTPUT_DIR / "google_trends_windows.csv", index=False)
    print(
        f"Detected {len(primary)} primary events, {len(alternate)} alternate "
        f"events, and {len(windows)} unique Trends windows"
    )


if __name__ == "__main__":
    main()
