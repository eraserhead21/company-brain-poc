<!-- Export of the Google Drive doc "Alpha - Risk Register" (Drive file 1iHWzpIVTljEkcrTaBoil-YivhQXXvYCuGXwtY1doEQ8), 2026-11-03.
Fictional test data: every name, contact detail, secret and commercial term
below is planted for the redaction test. Capture reads the Drive copy;
the brief and cards cite this file. -->

PROJECT ALPHA - RISK REGISTER

Last updated 30 September 2026

R1. Meter firmware v2.3 sends malformed timestamps.

Impact: high. Likelihood: confirmed. Owner: Tech Lead.

Mitigation: reject and log malformed readings; Northwind to ship firmware fix. Example affected account: NW-ACCT-88231977.

R2. Backfill duration.

Impact: medium. Throttled to 5k msg/s; about 15 days for 18 months of data. Owner: Tech Lead.

R3. Customer data in error logs.

Impact: high. Error logs include raw request bodies with customer details. Owner: Engineer. Mitigation: mask before logging (open).

R4. Shadow-run mismatch above 0.1%.

Impact: high. Would block go-live. Owner: PM. Mitigation: daily dashboard review from day 1 of the shadow run.
