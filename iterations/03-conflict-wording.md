# Round 3: conflict wording

- **Date:** 2026-11-03
- **Trigger:** review of round 2 by a person: "open conflicts, I'm not clear".
- **Run:** full rebuild from all sources (PR #11). The run prompt only says "follow `card-extractor.md`"; no extra rules in the prompt.
- **Score record:** `tests/results/r3-2026-11-03.json`

## What changed

Rule commit [3ce478a](https://github.com/eraserhead21/claude-org-poc/commit/3ce478a), added to `card-extractor.md`:

- "List a conflict only if acting on the wrong claim would change a decision, a design, an owner or a date someone plans against. Two wordings of when a past event happened are not a conflict. A planned date that a later source makes impossible, with no new date given, is a supersession."
- "When redaction turns different people into the same role, label each person with a letter (Engineer A, Engineer B)."

## Open conflicts, before and after

| Round 2 | Round 3 |
|---|---|
| Broker: Kafka vs Event Hubs | Broker: Kafka vs Event Hubs, "acting on the wrong one changes the design" |
| On-call owner: "one Engineer" vs "a different Engineer" | On-call owner: Engineer A vs Engineer B |
| Backfill end date 17 Oct vs about 15 days | Moved to Supersessions: "17 Oct no longer holds; no new date" |
| Duplicate fix merged "last week" vs "this week" | Dropped: not a conflict |

## Score

| Check | Round 1 | Round 2 | Round 3 |
|---|---|---|---|
| Redaction | 20/20 | 20/20 | 20/20 |
| Names | 0 | 0 | 0 |
| Hand checks | 8/12 | 11/12 | 11/12 |
| Open conflicts listed | 0 | 4 (2 noise) | 2 (0 noise) |

## What failed

- **C1 retention:** unchanged; still a supersession. Kept as a known gap by decision: the notes say "Agreed: ... 30 days", which the rule reads as a change.

## New problems seen

- One card restates a status change rather than a reusable lesson (`2026-09-30-go-live-moved-to-28-nov.md`). 11 cards, up from 9.

## Cost

- 105.2k Haiku tokens, 37 tool calls, 2m28s (round 2: 115.2k).

## Caveat

- Tuned against the same answer key as rounds 1 and 2. Rules are frozen after this round for the held-out test (round 4).
