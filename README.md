# Search Attention Around Bitcoin Price Surges

An event-based time-series study of whether Google search interest for Bitcoin
peaks before, during, or after objectively defined local price peaks.

## Status

**Analysis complete.** The predetermined analytical decisions are recorded in
`research_protocol.md`; the source-access change is disclosed in
`docs/deviations.md`.

## Research question

> Across objectively defined Bitcoin price-surge events, does Google search
> interest tend to peak before, during, or after the local price peak?

## Repository layout

```text
data/
  raw/          Untouched source exports (not overwritten)
  interim/      Validated and aligned intermediate data
  processed/    Analysis-ready tables
docs/           Source notes, data dictionaries, and decision records
figures/        Final publication-ready charts
notebooks/      Exploration and manual validation only
results/        Final event and summary tables
src/bitcoin_search_attention/
                 Reusable collection, validation, event, and analysis code
tests/           Automated tests for the analytical rules
```

## Result

The primary 100% threshold produced 7 qualifying events. Search attention
peaked before the local price peak in 5 events, in the same week in 1 event,
and after it in 1 event. The median lag was **-5 weeks** (IQR -7.5 to -2), so
the result does not support the predetermined hypothesis that attention would
generally peak at or after price.

At the locked 70% sensitivity threshold, 4 of 7 lags were negative and the
median lag was **-6 weeks**. The pattern remained earlier on average, although
it was more mixed. Three primary events and one alternate event have a peak on
an analysis-window boundary and must be interpreted cautiously.

## Data sources

- Bitcoin USD market data: CoinGecko official Historical Data CSV export.
- Search interest: Google Trends, using official Explore exports for historical
  coverage. Google Trends values measure relative, normalized interest rather
  than absolute search volume.

Source settings, retrieval dates, and raw-file checksums are recorded in
`docs/data_sources.md` and `data/raw/google_trends/manifest.json`.

## Reproduction

From an environment with the project and development dependencies installed,
run:

```powershell
python scripts/prepare_prices.py
python scripts/detect_price_events.py
python scripts/prepare_trends.py
python scripts/analyze_events.py
python scripts/create_figures.py
pytest
```

The target environment is Python 3.13 or newer. The official raw Google Trends
exports are already preserved in the repository, so reproduction does not
require an automated Trends client.

## Portfolio case study

The finished narrative will live as a dedicated page in the existing portfolio.
This repository will remain the technical and methodological record behind that
page.
