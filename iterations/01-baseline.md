# Round 1: baseline

- **Date:** 2026-10-01
- **Runs:** one full capture (PR #8), then one delta capture (PR #9). See `log.md`.
- **Output scored:** commit [741e4e7](https://github.com/eraserhead21/company-brain-poc/tree/741e4e7): 8 cards and the brief.
- **Score record:** `tests/results/r1-2026-10-01.json`

## Rules in force

- Extractor and capture skill from the scaffold, commit [7d69a91](https://github.com/eraserhead21/company-brain-poc/commit/7d69a91).
- Delta fixes during the day: GitHub timestamp cursor and skip own capture PRs ([d6c2dba](https://github.com/eraserhead21/company-brain-poc/commit/d6c2dba)); client-side Drive date check ([0adb64e](https://github.com/eraserhead21/company-brain-poc/commit/0adb64e)).
- `CLAUDE.md` already said: "When two sources disagree and neither supersedes the other, do not pick one." The extractor steps did not ask for an Open conflicts section.

## Score

| Check | Result |
|---|---|
| Redaction | 20/20 caught |
| Names | 0 leaked |
| Hand checks | **8/12** |

## What failed

- **C1 retention:** the brief said "30 days (originally 90)", as if settled. Not flagged.
- **C2 broker:** the brief said Event Hubs. The design doc's Kafka was neither flagged nor marked stale.
- **C3 on-call owner:** not mentioned at all.
- **L4 sandbox access:** the kickoff lesson ("request it at kickoff") had no card.

## Human review

- During PR review, three cards were edited by hand on GitHub before merge: [a0eeb1b](https://github.com/eraserhead21/company-brain-poc/commit/a0eeb1b), [aeace99](https://github.com/eraserhead21/company-brain-poc/commit/aeace99), [457099c](https://github.com/eraserhead21/company-brain-poc/commit/457099c). Merging the PR is the approval step.

## Cost

- Full capture: 58.8k Haiku tokens, 36 tool calls, 2m45s.
- Delta capture: 59.6k Haiku tokens.

## Read

- Redaction works. Conflict handling does not: the extractor merges disagreeing sources into one answer.
- Lint could not catch this either: a conflict missed at capture never reaches the wiki.
