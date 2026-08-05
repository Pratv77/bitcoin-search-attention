import json
from dataclasses import asdict
from pathlib import Path

from bitcoin_search_attention.prices import (
    load_coingecko_export,
    to_completed_weekly_closes,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "coingecko_btc_usd_2013-04-28_2026-08-04_retrieved_2026-08-04.csv"
)
WEEKLY_PATH = PROJECT_ROOT / "data" / "interim" / "bitcoin_weekly_prices.csv"
VALIDATION_PATH = PROJECT_ROOT / "data" / "interim" / "price_validation.json"


def serialize_validation(validation: object, freeze_week: object) -> dict[str, object]:
    record = asdict(validation)  # type: ignore[arg-type]
    record["earliest_date"] = validation.earliest_date.isoformat()  # type: ignore[attr-defined]
    record["latest_date"] = validation.latest_date.isoformat()  # type: ignore[attr-defined]
    record["missing_calendar_dates"] = [
        value.isoformat()
        for value in validation.missing_calendar_dates  # type: ignore[attr-defined]
    ]
    record["freeze_week"] = freeze_week.isoformat()  # type: ignore[attr-defined]
    return record


def main() -> None:
    daily, validation = load_coingecko_export(RAW_PATH)
    weekly, freeze_week = to_completed_weekly_closes(daily)
    WEEKLY_PATH.parent.mkdir(parents=True, exist_ok=True)
    weekly.to_csv(WEEKLY_PATH, index=False)
    VALIDATION_PATH.write_text(
        json.dumps(serialize_validation(validation, freeze_week), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(weekly)} completed weeks through {freeze_week.date()}")


if __name__ == "__main__":
    main()
