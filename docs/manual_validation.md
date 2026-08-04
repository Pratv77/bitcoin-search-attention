# Manual peak validation

Validation completed: 2026-08-04

All 14 event charts (7 primary and 7 alternate) were checked against the peak
weeks selected by the analysis code. Each marked price and search peak matches
the visible maximum under the locked earliest-tie rule. No source or
implementation correction was required.

## Boundary cases

| Event | Lag (weeks) | Boundary flag | Interpretation note |
|---|---:|---|---|
| P03 | +3 | search end | A later search maximum outside the window is possible. |
| P04 | 0 | price end; search end | Both observed maxima occur at the final week. |
| P05 | -5 | price end | A later price maximum outside the window is possible. |
| A07 | +3 | search end | A later search maximum outside the window is possible. |

Boundary cases remain included, as predetermined. They limit interpretation but
are not grounds for selective window extension or exclusion.

The full audit view is `figures/validation_sheet.png`; individual event charts
are in `figures/events/`.
