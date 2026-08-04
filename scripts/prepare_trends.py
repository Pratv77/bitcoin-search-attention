"""Validate Google Trends exports and build weekly attention series."""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from bitcoin_search_attention.trends import load_trends_export, to_weekly_interest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "google_trends"
WINDOWS_PATH = PROJECT_ROOT / "data" / "interim" / "google_trends_windows.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "interim" / "google_trends_weekly.csv"
VALIDATION_PATH = PROJECT_ROOT / "data" / "interim" / "trends_validation.json"
MANIFEST_PATH = RAW_DIR / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    windows = pd.read_csv(
        WINDOWS_PATH,
        parse_dates=[
            "trigger_week",
            "window_start",
            "window_end",
            "query_start",
            "query_end",
        ],
    )
    weekly_frames: list[pd.DataFrame] = []
    validation_records: list[dict[str, object]] = []

    for window in windows.itertuples(index=False):
        matches = sorted(RAW_DIR.glob(f"{window.query_id}_*.csv"))
        if len(matches) != 1:
            raise ValueError(f"{window.query_id}: expected exactly one raw export")
        source_path = matches[0]
        daily, validation = load_trends_export(
            source_path,
            query_id=window.query_id,
            expected_start=window.query_start,
            expected_end=window.query_end,
        )
        weekly_frames.append(to_weekly_interest(daily, query_id=window.query_id))
        record = asdict(validation)
        record["earliest_date"] = validation.earliest_date.isoformat()
        record["latest_date"] = validation.latest_date.isoformat()
        record["filename"] = source_path.name
        record["sha256"] = sha256(source_path)
        validation_records.append(record)

    weekly = pd.concat(weekly_frames, ignore_index=True)
    weekly.to_csv(OUTPUT_PATH, index=False)
    manifest_text = json.dumps(validation_records, indent=2) + "\n"
    VALIDATION_PATH.write_text(manifest_text, encoding="utf-8")
    MANIFEST_PATH.write_text(manifest_text, encoding="utf-8")
    print(f"Validated {len(validation_records)} exports and {len(weekly)} weekly rows")


if __name__ == "__main__":
    main()
