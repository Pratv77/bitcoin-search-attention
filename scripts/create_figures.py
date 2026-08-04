"""Create publication figures and event-level validation charts."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"

PRICE_COLOR = "#F7931A"
SEARCH_COLOR = "#2563EB"
BOUNDARY_COLOR = "#B45309"
TEXT_COLOR = "#172033"
GRID_COLOR = "#D8DEE9"


def relative_week(weeks: pd.Series, trigger: pd.Timestamp) -> pd.Series:
    return (weeks - trigger).dt.days // 7


def event_series(
    result: pd.Series,
    prices: pd.DataFrame,
    search: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    price_window = prices.loc[
        prices["week"].between(result["window_start"], result["window_end"])
    ].copy()
    search_window = search.loc[
        search["query_id"].eq(result["query_id"])
        & search["week"].between(result["window_start"], result["window_end"])
    ].copy()
    price_window["relative_week"] = relative_week(
        price_window["week"], result["trigger_week"]
    )
    search_window["relative_week"] = relative_week(
        search_window["week"], result["trigger_week"]
    )
    return price_window, search_window


def plot_event_chart(
    result: pd.Series,
    prices: pd.DataFrame,
    search: pd.DataFrame,
    destination: Path,
) -> None:
    price_window, search_window = event_series(result, prices, search)
    fig, price_axis = plt.subplots(figsize=(9, 4.8))
    search_axis = price_axis.twinx()

    price_axis.plot(
        price_window["relative_week"],
        price_window["price_usd"],
        color=PRICE_COLOR,
        linewidth=2.2,
        label="Bitcoin weekly close",
    )
    search_axis.plot(
        search_window["relative_week"],
        search_window["search_interest"],
        color=SEARCH_COLOR,
        linewidth=2.2,
        label="Weekly search interest",
    )
    price_peak_x = int((result["price_peak_week"] - result["trigger_week"]).days // 7)
    search_peak_x = int((result["search_peak_week"] - result["trigger_week"]).days // 7)
    price_axis.scatter(
        price_peak_x,
        result["price_peak_usd"],
        color=PRICE_COLOR,
        edgecolor="white",
        linewidth=1,
        s=70,
        zorder=5,
    )
    search_axis.scatter(
        search_peak_x,
        result["search_peak_interest"],
        color=SEARCH_COLOR,
        edgecolor="white",
        linewidth=1,
        s=70,
        zorder=5,
    )
    price_axis.axvline(0, color=TEXT_COLOR, linewidth=1.2, alpha=0.75)
    price_axis.axvspan(-8, -0.05, color=GRID_COLOR, alpha=0.22)
    price_axis.set_xlim(-8, 16)
    price_axis.set_xticks(np.arange(-8, 17, 4))
    price_axis.set_xlabel("Weeks relative to trigger")
    price_axis.set_ylabel("Bitcoin weekly close (USD)", color=PRICE_COLOR)
    search_axis.set_ylabel("Google search interest (0–100)", color=SEARCH_COLOR)
    search_axis.set_ylim(0, 105)
    price_axis.grid(axis="y", color=GRID_COLOR, linewidth=0.7)
    price_axis.set_title(
        f"{result['event_id']} · Trigger {result['trigger_week'].date()} · "
        f"Lag {result['peak_lag_weeks']:+d} weeks",
        loc="left",
        color=TEXT_COLOR,
        fontweight="bold",
    )
    price_axis.text(
        0.99,
        0.02,
        f"Boundary: {result['boundary_flag']}",
        transform=price_axis.transAxes,
        ha="right",
        va="bottom",
        color=BOUNDARY_COLOR if result["boundary_flag"] != "none" else TEXT_COLOR,
        fontsize=9,
    )
    for axis in (price_axis, search_axis):
        axis.spines["top"].set_visible(False)
    fig.tight_layout()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_lag_dotplot(results: pd.DataFrame, destination: Path) -> None:
    ordered = results.sort_values("trigger_week", ascending=True).reset_index(drop=True)
    y_positions = np.arange(len(ordered))
    boundary = ordered["price_boundary"] | ordered["search_boundary"]
    median = float(ordered["peak_lag_weeks"].median())

    fig, axis = plt.subplots(figsize=(9, 5.2))
    axis.axvline(0, color=TEXT_COLOR, linewidth=1.2)
    axis.axvline(median, color=SEARCH_COLOR, linestyle="--", linewidth=1.4)
    axis.scatter(
        ordered.loc[~boundary, "peak_lag_weeks"],
        y_positions[~boundary],
        s=70,
        color=SEARCH_COLOR,
        label="Complete interior peak",
        zorder=3,
    )
    axis.scatter(
        ordered.loc[boundary, "peak_lag_weeks"],
        y_positions[boundary],
        s=85,
        marker="D",
        facecolor="white",
        edgecolor=BOUNDARY_COLOR,
        linewidth=1.8,
        label="Boundary flagged",
        zorder=3,
    )
    for index, lag in enumerate(ordered["peak_lag_weeks"]):
        axis.annotate(
            f"{lag:+d}",
            (lag, index),
            xytext=(7, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=TEXT_COLOR,
        )
    axis.set_yticks(y_positions)
    axis.set_yticklabels(
        [
            f"{event_id}  {date.date()}"
            for event_id, date in zip(ordered["event_id"], ordered["trigger_week"])
        ]
    )
    axis.set_xlabel("Search peak minus price peak (weeks)")
    axis.set_title(
        "Peak-attention lag across primary Bitcoin surge events",
        loc="left",
        color=TEXT_COLOR,
        fontweight="bold",
    )
    axis.text(
        median,
        0.35,
        f" Median = {median:+.0f} weeks",
        color=SEARCH_COLOR,
        va="bottom",
        fontsize=9,
    )
    axis.set_xlim(min(-11, ordered["peak_lag_weeks"].min() - 2), 5)
    axis.grid(axis="x", color=GRID_COLOR, linewidth=0.7)
    axis.legend(frameon=False, loc="lower right")
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0)
    fig.tight_layout()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_validation_sheet(
    all_results: pd.DataFrame,
    prices: pd.DataFrame,
    search: pd.DataFrame,
    destination: Path,
) -> None:
    fig, axes = plt.subplots(7, 2, figsize=(13, 21), sharex=True)
    for axis, (_, result) in zip(axes.flat, all_results.iterrows()):
        price_window, search_window = event_series(result, prices, search)
        price_scaled = price_window["price_usd"] / price_window["price_usd"].max()
        search_scaled = (
            search_window["search_interest"] / search_window["search_interest"].max()
        )
        axis.plot(
            price_window["relative_week"],
            price_scaled,
            color=PRICE_COLOR,
            linewidth=1.8,
        )
        axis.plot(
            search_window["relative_week"],
            search_scaled,
            color=SEARCH_COLOR,
            linewidth=1.8,
        )
        price_peak_x = int(
            (result["price_peak_week"] - result["trigger_week"]).days // 7
        )
        search_peak_x = int(
            (result["search_peak_week"] - result["trigger_week"]).days // 7
        )
        axis.scatter(price_peak_x, 1, color=PRICE_COLOR, s=35, zorder=3)
        axis.scatter(search_peak_x, 1, color=SEARCH_COLOR, s=35, zorder=3)
        axis.axvline(0, color=TEXT_COLOR, linewidth=0.8, alpha=0.7)
        axis.set_title(
            f"{result['event_id']} · {result['trigger_week'].date()} · "
            f"lag {result['peak_lag_weeks']:+d} · {result['boundary_flag']}",
            loc="left",
            fontsize=10,
        )
        axis.set_xlim(-8, 16)
        axis.set_ylim(0, 1.08)
        axis.grid(color=GRID_COLOR, linewidth=0.5)
        axis.spines[["top", "right"]].set_visible(False)
    axes[-1, 0].set_xlabel("Weeks relative to trigger")
    axes[-1, 1].set_xlabel("Weeks relative to trigger")
    fig.suptitle(
        "Manual peak-validation sheet · orange price · blue search attention",
        x=0.07,
        ha="left",
        fontsize=15,
        fontweight="bold",
        color=TEXT_COLOR,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    prices = pd.read_csv(
        INTERIM_DIR / "bitcoin_weekly_prices.csv", parse_dates=["week", "source_date"]
    )
    search = pd.read_csv(INTERIM_DIR / "google_trends_weekly.csv", parse_dates=["week"])
    date_columns = [
        "trigger_week",
        "window_start",
        "window_end",
        "price_peak_week",
        "search_peak_week",
    ]
    primary = pd.read_csv(
        RESULTS_DIR / "event_results_primary.csv", parse_dates=date_columns
    )
    alternate = pd.read_csv(
        RESULTS_DIR / "event_results_alternate.csv", parse_dates=date_columns
    )
    all_results = pd.concat([primary, alternate], ignore_index=True).sort_values(
        ["analysis", "trigger_week"], ascending=[False, True], ignore_index=True
    )

    plot_lag_dotplot(primary, FIGURES_DIR / "lag_dotplot_primary.png")
    for _, result in all_results.iterrows():
        plot_event_chart(
            result,
            prices,
            search,
            FIGURES_DIR / "events" / f"{result['event_id']}.png",
        )
    plot_validation_sheet(
        all_results, prices, search, FIGURES_DIR / "validation_sheet.png"
    )
    print(f"Created {len(all_results) + 2} figures")


if __name__ == "__main__":
    main()
