from pathlib import Path

import pandas as pd

from bitcoin_search_attention.trends import load_trends_export, to_weekly_interest


def test_load_and_aggregate_complete_export(tmp_path: Path) -> None:
    dates = pd.date_range("2020-01-06", periods=175, freq="D")
    csv_path = tmp_path / "trends.csv"
    rows = ["Category: All categories", "", "Day,Bitcoin: (Worldwide)"]
    rows.extend(f"{date.date()},{index % 101}" for index, date in enumerate(dates))
    csv_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    daily, validation = load_trends_export(
        csv_path,
        query_id="GT01",
        expected_start=pd.Timestamp("2020-01-06", tz="UTC"),
        expected_end=pd.Timestamp("2020-06-28", tz="UTC"),
    )
    weekly = to_weekly_interest(daily, query_id="GT01")

    assert validation.row_count == 175
    assert len(weekly) == 25
    assert weekly["daily_observations"].eq(7).all()
    assert weekly.loc[0, "week"] == pd.Timestamp("2020-01-12", tz="UTC")
