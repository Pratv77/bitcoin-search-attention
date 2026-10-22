# Search Attention Around Bitcoin Price Surges

A rule-based event study of when worldwide Google search attention reaches its
highest point during major Bitcoin price surges.

## Research question

Across objectively defined Bitcoin surge events, does search attention peak
before, during, or after the local price maximum?

## Main result

Seven events qualified under the primary 100% surge threshold. Search attention
peaked before price in five events, in the same week in one, and after price in
one. The median peak timing difference was five weeks before price.

With only seven events, this direction is not statistically distinguishable
from chance. The result is descriptive, not a trading signal, forecast, or
causal relationship.

At the 70% sensitivity threshold, four events placed search before price and
three placed it after price. The median remained six weeks before price, but the
event-level results became more mixed.

## Method at a glance

- Bitcoin prices are weekly closing prices from CoinGecko.
- Search attention comes from the worldwide Bitcoin topic in Google Trends.
- A primary event begins when price crosses from below to at least 100% above
  its lowest weekly close from the previous 52 complete weeks.
- Every event uses the same 25-week window: eight weeks before the trigger, the
  trigger week, and sixteen weeks after it.
- **Peak timing difference** is the week of peak search attention minus the week
  of the local price maximum.
- The full analysis is repeated with a 70% threshold as a sensitivity test.

The research question, event rules, measurements, and sensitivity threshold
were recorded in `research_protocol.md` before the event-level search results
were examined.

## Repository guide

- [`research_protocol.md`](research_protocol.md): predetermined research and
  analysis rules.
- [`docs/data_sources.md`](docs/data_sources.md): sources, coverage, and Google
  Trends normalization.
- [`results/event_results_primary.csv`](results/event_results_primary.csv): one
  row for each primary event and its measured peaks.
- [`results/threshold_comparison.csv`](results/threshold_comparison.csv): summary
  comparison of the 100% and 70% thresholds.
- [`figures/events/`](figures/events/): individual charts for all 14 primary and
  sensitivity events.
- [`src/bitcoin_search_attention/`](src/bitcoin_search_attention/): analysis
  functions.
- [`tests/`](tests/): automated checks for the main analytical rules.

## Reproduce the analysis

Python 3.13 or newer is required. The raw source exports used in the study are
included in the repository.

On Windows, some raw data file names are long enough to fail on checkout. Run
`git config --global core.longpaths true` before cloning.

```text
python -m pip install -e ".[dev]"
python scripts/prepare_prices.py
python scripts/detect_price_events.py
python scripts/prepare_trends.py
python scripts/analyze_events.py
python scripts/create_figures.py
python -m pytest
```
