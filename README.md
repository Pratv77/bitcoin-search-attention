# Search Attention Around Bitcoin Price Surges

An event-based time-series study of whether Google search interest for Bitcoin
peaks before, during, or after objectively defined local price peaks.

## Status

**Protocol locked.** The predetermined analytical decisions are recorded in
`research_protocol.md`. Any later methodological change must be documented as a
protocol deviation rather than silently replacing the original rule.

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

## Planned workflow

1. Lock and commit the research protocol.
2. Collect and preserve price and attention data.
3. Validate dates, weekly alignment, missing values, and duplicates.
4. Identify events using the locked rule.
5. Measure price and attention peaks.
6. Produce the predetermined summaries and figures.
7. Repeat the full pipeline using the single alternate threshold.
8. Export final assets for the portfolio case-study page.

## Data sources

- Bitcoin USD market data: CoinGecko API.
- Search interest: Google Trends, using official Explore exports for historical
  coverage. Google Trends values measure relative, normalized interest rather
  than absolute search volume.

Source settings, retrieval dates, and raw-file checksums will be recorded in a
collection manifest. Credentials must stay in a local `.env` file and are never
committed.

## Reproduction

Reproduction commands will be added as each pipeline stage is implemented. The
target environment is Python 3.13 or newer.

## Portfolio case study

The finished narrative will live as a dedicated page in the existing portfolio.
This repository will remain the technical and methodological record behind that
page.
