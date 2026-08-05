# Data sources

The repository preserves the original source exports used in the analysis.

## CoinGecko

- Source: official CoinGecko Historical Data CSV for Bitcoin in USD.
- Retrieved: 2026-08-04.
- Coverage: 2013-04-28 through 2026-08-04.
- Analysis input: 693 completed Sunday-ending weekly closes through 2026-08-02.
- Validation: no duplicate dates or nonpositive prices. Three isolated calendar
  dates were missing, but none affected a Sunday closing price.

## Google Trends

- Source: official Google Trends Explore exports for the worldwide Bitcoin topic
  `/m/05p0rrx`, using Web Search and all categories.
- Retrieved: 2026-08-04.
- Collection: 14 event windows with 175 daily values each, covering exactly 25
  complete Monday-to-Sunday weeks.
- Weekly measure: the mean of the seven daily interest values.
- Analysis input: 350 complete event-week observations with no missing or
  duplicated values.

Google Trends scales each export independently from 0 to 100. The analysis can
therefore compare peak timing within an event, but not search levels across
separate exports. File names, date ranges, validation results, and checksums are
recorded in `data/raw/google_trends/manifest.json`.
