# The rule bank's trend

Written by `scripts/bank_trend.py` from `evals/bank/ledger.jsonl` and the bank; do not edit here: run the script. `scripts/bank_trend.py --check` is in the fast loop and fails when this page is stale.

A trend is a light the plant grows towards, never a gate (SC-023): no rule fails a run, a signal is acted on by triage, and the one red is a door fault. One failure is noise. A rule is a **signal** when it failed in at least three of its last five samplings, in two of its last five for a `safety` rule (design 5.3). The check model's agreement with one of those failures is part of 5.3 and is not yet in the ledger's line (design 5.1), so the watch list below is by the failure count alone.

No run has been recorded yet; the ledger keeps a window of the last 60 runs, and the first live run is by hand.

## The families

### ask

Not sampled yet.

### pace

Not sampled yet.

### safety

Not sampled yet.

### track

Not sampled yet.

## The watch list

No rule is a signal.

None left the list since the previous page.

## The grader

No run yet.

## The cost

No run yet.
