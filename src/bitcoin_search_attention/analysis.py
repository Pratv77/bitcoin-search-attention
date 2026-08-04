"""Event-level peak measurements and predetermined summaries."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class EventResult:
    analysis: str
    event_id: str
    query_id: str
    trigger_week: pd.Timestamp
    window_start: pd.Timestamp
    window_end: pd.Timestamp
    price_peak_week: pd.Timestamp
    price_peak_usd: float
    search_peak_week: pd.Timestamp
    search_peak_interest: float
    peak_lag_weeks: int
    price_at_search_peak_usd: float
    price_position_pct: float
    price_tie_count: int
    search_tie_count: int
    price_boundary: bool
    search_boundary: bool
    boundary_flag: str


def measure_event(
    event: pd.Series,
    *,
    query_id: str,
    weekly_prices: pd.DataFrame,
    weekly_search: pd.DataFrame,
) -> EventResult:
    """Apply the locked event measurements to one complete event."""
    prices = weekly_prices.sort_values("week", ignore_index=True)
    search = weekly_search.loc[weekly_search["query_id"].eq(query_id)].sort_values(
        "week", ignore_index=True
    )
    full_price_window = prices.loc[
        prices["week"].between(event["window_start"], event["window_end"])
    ]
    price_peak_area = full_price_window.loc[
        full_price_window["week"].between(event["trigger_week"], event["window_end"])
    ]
    search_window = search.loc[
        search["week"].between(event["window_start"], event["window_end"])
    ]

    if len(full_price_window) != 25 or len(search_window) != 25:
        raise ValueError(f"{event['event_id']}: incomplete 25-week event window")
    if len(price_peak_area) != 17:
        raise ValueError(f"{event['event_id']}: incomplete price-peak area")

    price_maximum = float(price_peak_area["price_usd"].max())
    price_ties = price_peak_area.loc[price_peak_area["price_usd"].eq(price_maximum)]
    price_peak = price_ties.iloc[0]

    search_maximum = float(search_window["search_interest"].max())
    search_ties = search_window.loc[search_window["search_interest"].eq(search_maximum)]
    search_peak = search_ties.iloc[0]
    price_at_search_peak = float(
        full_price_window.loc[
            full_price_window["week"].eq(search_peak["week"]), "price_usd"
        ].iloc[0]
    )

    lag_weeks = int((search_peak["week"] - price_peak["week"]).days // 7)
    price_position = (price_at_search_peak / price_maximum - 1) * 100
    price_boundary = bool(
        price_peak["week"] in (event["trigger_week"], event["window_end"])
    )
    search_boundary = bool(
        search_peak["week"] in (event["window_start"], event["window_end"])
    )
    boundary_parts = []
    if price_peak["week"] == event["trigger_week"]:
        boundary_parts.append("price_start")
    if price_peak["week"] == event["window_end"]:
        boundary_parts.append("price_end")
    if search_peak["week"] == event["window_start"]:
        boundary_parts.append("search_start")
    if search_peak["week"] == event["window_end"]:
        boundary_parts.append("search_end")

    return EventResult(
        analysis=event["analysis"],
        event_id=event["event_id"],
        query_id=query_id,
        trigger_week=event["trigger_week"],
        window_start=event["window_start"],
        window_end=event["window_end"],
        price_peak_week=price_peak["week"],
        price_peak_usd=price_maximum,
        search_peak_week=search_peak["week"],
        search_peak_interest=search_maximum,
        peak_lag_weeks=lag_weeks,
        price_at_search_peak_usd=price_at_search_peak,
        price_position_pct=price_position,
        price_tie_count=len(price_ties),
        search_tie_count=len(search_ties),
        price_boundary=price_boundary,
        search_boundary=search_boundary,
        boundary_flag="+".join(boundary_parts) if boundary_parts else "none",
    )


def results_frame(results: list[EventResult]) -> pd.DataFrame:
    """Convert event result records to a chronologically sorted table."""
    return pd.DataFrame([asdict(result) for result in results]).sort_values(
        "trigger_week", ignore_index=True
    )


def summarize_results(results: pd.DataFrame) -> dict[str, float | int]:
    """Calculate only the summaries predetermined in the protocol."""
    lags = results["peak_lag_weeks"]
    negative = int(lags.lt(0).sum())
    zero = int(lags.eq(0).sum())
    positive = int(lags.gt(0).sum())
    count = len(results)
    return {
        "qualifying_events": count,
        "median_lag_weeks": float(lags.median()),
        "lag_q1_weeks": float(lags.quantile(0.25)),
        "lag_q3_weeks": float(lags.quantile(0.75)),
        "minimum_lag_weeks": int(lags.min()),
        "maximum_lag_weeks": int(lags.max()),
        "negative_lags": negative,
        "zero_lags": zero,
        "positive_lags": positive,
        "negative_proportion": negative / count,
        "zero_proportion": zero / count,
        "positive_proportion": positive / count,
        "at_or_after_zero_proportion": (zero + positive) / count,
        "median_price_position_pct": float(results["price_position_pct"].median()),
        "boundary_flagged_events": int(
            (results["price_boundary"] | results["search_boundary"]).sum()
        ),
    }
