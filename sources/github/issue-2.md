<!-- Snapshot of GitHub issue #2 in eraserhead21/company-brain-poc, taken 2026-11-12 by scripts/snapshot_github.py.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads GitHub;
the brief and cards cite the URL, and the checks read this file. -->

ISSUE 2: DST change double-counts one hour

Created: 2026-10-01. State: closed.

Readings between 02:00 and 03:00 on 25 Oct 2026 exist twice in meter local time. Aggregates for that day are about 4% high in the test replay.

Comment, 2026-10-01:

Resolution: store all readings in UTC, convert to local only in the billing export. See ADR-001.
