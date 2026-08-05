# Search Attention Around Bitcoin Price Surges

## Protocol status

**LOCKED**

Version: 1.0  
Prepared: 2026-08-04  
Lock date: 2026-08-04

No event-level search results, peak-timing results, or threshold comparisons were
examined before this document was marked **LOCKED**. Corrections after locking
must be recorded in `docs/deviations.md`; the original rule must remain visible.

## Research question

Across objectively defined Bitcoin price-surge events, does Google search
interest tend to peak before, during, or after the local price peak?

## Predetermined hypothesis

Google search interest will generally peak at or after the local Bitcoin price
peak during substantial price-surge events.

## Study classification

Observational, correlational, event-based time-series analysis.

## Data scope

### Bitcoin price

- Source: CoinGecko API, coin ID `bitcoin`.
- Currency: USD.
- Retained field: price.
- Source frequency: daily observations at approximately 00:00 UTC.
- Weekly measure: the last available daily price in each Sunday-ending UTC week.
- Earliest eligible date: the first week for which 52 complete prior weekly
  observations are available in the overlapping source data.

### Search attention

- Source: Google Trends Explore official export.
- Concept: Bitcoin topic (the exact Google topic identifier must be recorded in
  the collection manifest before the first export).
- Geography: worldwide.
- Category: all categories.
- Search property: Web Search.
- Weekly measure: mean of the available daily interest values in each
  Sunday-ending week when the export is daily; otherwise the exported weekly
  value.
- Interpretation: a normalized index of relative search interest, not absolute
  search volume.

### Study period and freeze rule

The study begins at the earliest complete overlapping week. The data freeze is
the most recent fully completed Sunday-ending week available from both sources
on the collection date. To guarantee the complete post-trigger window, a trigger
is eligible only if it occurs at least 16 complete weeks before the data freeze.
Exact source and eligible dates will be inserted without changing this rule.

## Event definition

### Primary rule

- Primary rise threshold: **100%**.
- Trailing-low period: **52 complete weeks**.
- Trigger: the first Sunday-ending week whose closing price crosses from below
  to at least 100% above the minimum weekly closing price in the preceding 52
  complete weeks. The current week is excluded from the trailing minimum. A
  week that remains above the threshold without a new crossing is not a trigger.
- Cooldown and merge period: **25 weeks**, covering the trigger week through
  week +24. Any additional threshold crossing in that interval belongs to the
  same event; the first trigger date is retained.
- A new event may begin on week +25 or later, ensuring that fixed 25-week event
  windows do not overlap.
- Minimum coverage: all 25 weekly price observations and all 25 weekly search
  observations from week −8 through week +16 must be present. Ineligible events
  remain in the exclusion log with a reason.

Complete rule:

> A price-surge event begins in the first Sunday-ending week when Bitcoin’s
> closing price crosses from below to at least 100% above the minimum weekly
> closing price from the preceding 52 complete weeks. Additional threshold
> crossings occurring during the next 24 weeks are treated as part of the same
> event.

### Sensitivity rule

Repeat the complete event-identification and measurement pipeline at a **70%**
threshold. Every other decision remains unchanged. No additional thresholds may
be introduced because of the observed result.

## Observation window

- Pre-trigger period: 8 weeks.
- Post-trigger period: 16 weeks.
- Total window: 25 weeks including the trigger week.
- Weeks considered for the local price maximum: trigger week through week +16.
- Weeks considered for peak search attention: week −8 through week +16.
- No event receives a selective extension or early termination.

## Peak and edge-case rules

- Local price maximum: highest weekly closing price from the trigger week through
  week +16.
- Peak search attention: highest weekly search-interest value in the full event
  window.
- Tied maxima: use the earliest tied week and record a tie flag plus the number
  of tied weeks. This deterministic choice applies to both series.
- Price boundary flag: the local price maximum occurs in the trigger week or
  week +16.
- Search boundary flag: peak search attention occurs in week −8 or week +16.
- Any boundary flag limits interpretation but does not automatically exclude the
  event.
- Missing weekly attention or price data causes exclusion under the complete-case
  rule; values are not interpolated for the primary analysis.
- Every detected peak will be checked against its event chart before results are
  finalized. Manual checking may identify implementation or source errors but
  may not replace a peak selected by the locked rule.

## Primary measurements

1. **Peak timing difference:** week of peak search attention minus week of the
   local price maximum, in whole weeks.
2. **Price position at peak attention:**

   `(price in the week of peak search attention / local maximum price - 1) × 100`

   A value of −20% means the price was 20% below the event’s local maximum when
   search attention peaked.

Interpretation of the peak timing difference:

- Negative: search attention peaked before price.
- Zero: both peaked in the same Sunday-ending week.
- Positive: search attention peaked after price.

## Predetermined summaries

- Number of qualifying and excluded events.
- Median peak timing difference.
- Interquartile range and full range of peak timing differences.
- Counts and proportions of negative, zero, and positive lags.
- Proportion of events at or after zero.
- Median price position at peak attention.
- Number of boundary-flagged events.
- Event counts by calendar period for descriptive context.

## Primary outputs

- Complete trigger and exclusion logs.
- Final event-results table.
- Horizontal event-level peak timing dot plot with a zero reference, median
  marker, and distinguished boundary cases.
- One event-selection illustration.
- One annotated measurement example.
- Two or three transparently selected illustrative event charts.
- Primary-versus-alternate threshold comparison table.

## Interpretation constraints

This design measures association and timing, not causation, investor identity,
purchase behaviour, profit, or loss. Google Trends magnitude is not compared
across independently normalized event exports; only within-event peak timing is
used. Results will be reported even if they contradict the hypothesis.

## Locked decisions

1. A 100% primary threshold and 70% alternate threshold.
2. A 52-week trailing-low period.
3. A 25-week non-overlap/merge rule.
4. The worldwide Bitcoin **topic**, rather than the literal search term.
5. Weekly closing price, rather than weekly mean price.
6. Earliest-tied-maximum handling with an explicit tie flag.

## Observed source coverage (added after collection)

The untouched CoinGecko export covers 2013-04-28 through 2026-08-04, with 693
complete Sunday-ending price weeks through the 2026-08-02 data freeze. The
earliest Google Trends event export begins 2015-09-07. Eligible primary triggers
run from 2015-12-13 through 2025-07-13, and every retained event has all 25
required price and search weeks. These observed dates instantiate the locked
coverage rule; they do not change it.
