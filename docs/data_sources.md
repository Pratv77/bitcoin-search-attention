# Data-source record

This document will be completed during collection. Raw files must never be
silently replaced; each retrieval gets a dated filename and a manifest entry.

## CoinGecko

- Coin ID: `bitcoin`
- Quote currency: `usd`
- Retrieval method: official CoinGecko Historical Data CSV export
- Historical Data page: `https://www.coingecko.com/en/coins/bitcoin/historical_data`
- API limitation: the free Demo API provides at most one year of historical
  market-chart data; see `docs/deviations.md`
- Retrieval date/time (UTC): 2026-08-04 19:41:39 UTC
- Returned coverage: 2013-04-28 through 2026-08-04; the current-day row has
  no closing price and is excluded before weekly aggregation
- Raw filename:
  `coingecko_btc_usd_2013-04-28_2026-08-04_retrieved_2026-08-04.csv`
- SHA-256:
  `b659d8720185a5fcfe3767972f1e585f3f4bdffb49670ce5fa6a8c40ae67a74e`
- Completed weekly coverage: 693 Sunday-ending weeks from 2013-04-28 through
  the data-freeze week of 2026-08-02
- Validation findings: no duplicated dates, no nonpositive closing prices,
  three isolated missing calendar dates (2013-06-04, 2015-01-28, and
  2022-05-23), and no missing Sunday close caused by those gaps

## Google Trends

- Access method: official Google Trends Explore CSV export
- Concept: Bitcoin topic, identifier `/m/05p0rrx` (Bitcoin, Cryptocurrency)
- Geography: worldwide
- Category: all categories
- Search property: Web Search
- Retrieval date (UTC): 2026-08-04
- Export design: 14 fixed event-query windows, each spanning Monday through
  Sunday for 175 daily observations and exactly 25 complete Sunday-ending weeks
- Weekly aggregation: arithmetic mean of the seven daily interest values in
  each Sunday-ending week
- Validated output: 350 event-week observations; no missing values, duplicate
  dates, incomplete weeks, or values outside the 0-100 index range
- Raw filenames, date ranges, row counts, validation fields, and SHA-256 values:
  `data/raw/google_trends/manifest.json`

Each export is independently normalized by Google Trends. The analysis therefore
uses only the timing of the peak inside each event window and does not compare
interest magnitudes across different exports.

The limited-access Google Trends API is not assumed to be available and its
rolling five-year window is insufficient for the intended full-history study.
