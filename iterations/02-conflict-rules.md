# Round 2: conflict rules

- **Date:** 2026-11-03
- **Run:** full rebuild. Old cards and brief removed, cursor reset to 2026-01-01, every source re-read (PR #10).
- **Output scored:** commit [7ef0ddd](https://github.com/eraserhead21/claude-org-poc/tree/7ef0ddd): 9 cards and the brief.
- **Score record:** `tests/results/r2-2026-11-03.json`

## What changed

1. **Brief format** ([741e4e7](https://github.com/eraserhead21/claude-org-poc/commit/741e4e7)): fixed sections, including Open conflicts and Supersessions. Every fact carries its source in brackets.
2. **Conflict and lesson rules** ([7ef0ddd](https://github.com/eraserhead21/claude-org-poc/commit/7ef0ddd)), added to `card-extractor.md`:
   - Before: "Rewrite `brief.md` ... keep what is still true, update what changed."
   - After, added: "Before you write it, list every claim that two sources state differently (a number, a date, a tool, an owner). A later source that states a change ("moved to", "now", "replaces", "agreed") is a supersession. Anything else is an open conflict. A later ADR that picks a different option than an earlier design doc is a conflict unless the ADR says it replaces the doc."
   - Added: "A lesson stated in meeting notes ... is a learning card, even if it is small."
   - Added: "Before you return, check that no fact in the brief contradicts a card."
3. **Citations** ([e88f67d](https://github.com/eraserhead21/claude-org-poc/commit/e88f67d)): Drive docs exported to `sources/`; cards and brief cite those paths, so links work in the public repo.

## Score

| Check | Round 1 | Round 2 |
|---|---|---|
| Redaction | 20/20 | 20/20 |
| Names | 0 | 0 |
| Hand checks | 8/12 | **11/12** |

## What failed

- **C1 retention:** recorded as a supersession (90 to 30 days), not an open conflict. Cause: the new rule lists "agreed" as a change word, and the notes say "Agreed: ... 30 days".

## New problems seen

- **Hard to read:** the on-call conflict says "one Engineer" versus "a different Engineer". Redaction removed the names, so the reader cannot tell who is who.
- **Noise:** 2 of the 4 listed conflicts do not need a person to act: a stale backfill end date, and "merged last week" versus "merged this week".
- **Cost doubled:** 115.2k Haiku tokens (round 1: 58.8k), 40 tool calls, 2m59s.

## Real findings the extractor raised

- ADR-001 puts the repeated DST hour at 02:00 to 03:00; `handler.py` uses Europe/London, where it is 01:00 to 02:00. No source states the meter time zone.
- No merged PR exists for the duplicate fix; issue 1 is its only evidence.

## Caveat

- These rules were written after seeing the round 1 misses, against the same answer key. This round shows the fix works on the known test. It is not a held-out result.
