# Protocol deviations

This file retains a dated, append-only explanation of changes made after the
protocol was locked.

## 2026-08-04 — CoinGecko retrieval method

The locked protocol specified collection through the CoinGecko API. After the
protocol was committed, current official access limits were verified: the free
Demo API provides at most one year of historical market-chart data, while the
study requires full history. The price source remains CoinGecko, but the data
will be retrieved through CoinGecko's official Historical Data CSV export,
which CoinGecko documents as the free method for a one-off historical download.

This is a source-access change only. It does not alter the USD price field,
weekly closing-price construction, study period rule, event definition,
thresholds, observation windows, peak rules, or predetermined summaries. The
untouched export, retrieval time, selected date range, and SHA-256 checksum will
be preserved.
