<!-- Snapshot of GitHub pull request #7 in eraserhead21/company-brain-poc, taken 2026-11-12 by scripts/snapshot_github.py.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads GitHub;
the brief and cards cite the URL, and the checks read this file. -->

PULL REQUEST 7: Throttle backfill publisher to 5k msg/s

Merged: 2026-10-01. State: merged.

Fixes #3. The one-month test ran at 3x the estimate because the broker throttled us near 5k msg/s. This caps the publisher at 5k msg/s. Full 18-month backfill now planned at about 15 days, not 5. Lesson: plan backfills from a measured test, not an estimate.
