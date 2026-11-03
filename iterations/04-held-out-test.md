# Round 4: held-out test

- **Date:** 2026-11-03
- **Question:** do the round 3 rules work on documents nobody tuned them against?
- **Run:** normal delta capture (PR #13). Read only what changed after the round 3 cursor.
- **Rules:** frozen at [3ce478a](https://github.com/eraserhead21/claude-org-poc/commit/3ce478a). No rule change in this round.
- **Score records:** `tests/results/r4-holdout-2026-11-03.json` (new key), `tests/results/r4-regression-2026-11-03.json` (original key).

## How the held-out test was built

- The answer key (`tests/answers/holdout.json`) was written before the new sources were published and before any run saw them.
- New sources, in the same style as the originals: two Drive docs ([Weekly 10-13](../sources/alpha-meeting-notes-2026-10-13-weekly.md), [Status 10-15](../sources/alpha-status-update-2026-10-15.md)) and GitHub issue #12.
- Planted: 6 confidential values of new kinds (contractor day rate, private email, sick leave, staging password, customer account, change-request price), 1 new name, 2 conflicts, 2 supersessions, 2 lessons.
- One trap: the same date written two ways ("started Monday" and "started 12 October"). It must not be listed as a conflict.

## Score

| Check | Held-out key | Original key (regression) |
|---|---|---|
| Redaction | 6/6 | 20/20 |
| Names | 0 | 0 |
| Hand checks | **7/7** | 11/12 (C1 known gap, unchanged) |

## What it got right

- Both conflicts listed with both sources: billing export interval (5 vs 15 minutes) and shadow-run sign-off owner (Tech Lead vs PM).
- Both supersessions recorded; Key dates show the new dates (shadow run 19 Nov, firmware 27 Oct).
- Both lessons became cards: ask for the customer's change-freeze calendar at kickoff; align the comparison day boundary before a shadow run.
- The trap: "started Monday" vs "started 12 October" was not listed.
- Delta mode: the Drive date filter returned 2 old files again; the client-side date check dropped them (`drive_filtered_out=2`).

## New problem seen

- **The 600-word cap pushes history out.** To fit, the brief dropped older supersession lines (go-live 14 to 28 Nov, backfill 5 to 15 days). The cards still hold them, but the brief loses its history as the project grows. A fix would move superseded history to a separate page; not done, because rules are frozen for this round.

## Cost

- 92.8k Haiku tokens, 23 tool calls, 1m55s, for a delta of 2 Drive docs and 1 issue.

## Caveat

- One held-out set, written by the same person who wrote the rules. It shows the rules carry over to new documents of the same kind. It does not prove they work on a real company's documents.
