"""Run the locked event measurements and predetermined summaries."""

import json
from pathlib import Path

import pandas as pd

from bitcoin_search_attention.analysis import (
    measure_event,
    results_frame,
    summarize_results,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
RESULTS_DIR = PROJECT_ROOT / "results"


def query_mapping(windows: pd.DataFrame) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for window in windows.itertuples(index=False):
        for event_id in window.event_ids.split("+"):
            mapping[event_id] = window.query_id
    return mapping


def analyze_set(
    events: pd.DataFrame,
    *,
    mapping: dict[str, str],
    prices: pd.DataFrame,
    search: pd.DataFrame,
) -> pd.DataFrame:
    measured = [
        measure_event(
            event,
            query_id=mapping[event["event_id"]],
            weekly_prices=prices,
            weekly_search=search,
        )
        for _, event in events.iterrows()
    ]
    return results_frame(measured)


def main() -> None:
    date_columns = ["trigger_week", "window_start", "window_end"]
    primary_events = pd.read_csv(
        INTERIM_DIR / "price_events_primary.csv", parse_dates=date_columns
    )
    alternate_events = pd.read_csv(
        INTERIM_DIR / "price_events_alternate.csv", parse_dates=date_columns
    )
    windows = pd.read_csv(INTERIM_DIR / "google_trends_windows.csv")
    prices = pd.read_csv(
        INTERIM_DIR / "bitcoin_weekly_prices.csv", parse_dates=["week", "source_date"]
    )
    search = pd.read_csv(INTERIM_DIR / "google_trends_weekly.csv", parse_dates=["week"])
    mapping = query_mapping(windows)

    primary = analyze_set(primary_events, mapping=mapping, prices=prices, search=search)
    alternate = analyze_set(
        alternate_events, mapping=mapping, prices=prices, search=search
    )
    summaries = {
        "primary": summarize_results(primary),
        "alternate": summarize_results(alternate),
    }
    comparison = pd.DataFrame(
        [
            {
                "analysis": label,
                "threshold_pct": 100 if label == "primary" else 70,
                "qualifying_events": summary["qualifying_events"],
                "median_lag_weeks": summary["median_lag_weeks"],
                "at_or_after_zero_proportion": summary["at_or_after_zero_proportion"],
                "median_price_position_pct": summary["median_price_position_pct"],
                "boundary_flagged_events": summary["boundary_flagged_events"],
            }
            for label, summary in summaries.items()
        ]
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    primary.to_csv(RESULTS_DIR / "event_results_primary.csv", index=False)
    alternate.to_csv(RESULTS_DIR / "event_results_alternate.csv", index=False)
    comparison.to_csv(RESULTS_DIR / "threshold_comparison.csv", index=False)
    (RESULTS_DIR / "summary_statistics.json").write_text(
        json.dumps(summaries, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
