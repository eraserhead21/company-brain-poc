# Round 6: a contested value is never a settled fact

- **Date:** 2026-11-13
- **Question:** when two documents disagree and no person has decided, does the brief keep both values out of its Decisions?
- **Issue:** claude-vault#139. A person found the defect while marking round 5 by hand.
- **Runs:** two delta runs on the same 2 unseen documents, in staged mode, each in a fresh Haiku agent. One used the new rules. One was a control with the round 5 rules.
- **Rules:** [a1bc76f](https://github.com/eraserhead21/company-brain-poc/commit/a1bc76f), frozen before the key and the unseen documents were added.
- **Score records:** `tests/results/r6-holdout-2026-11-13.json`, `r6-control-2026-11-13.json`, `r6-regression-2026-11-13.json`, `r6-regression-holdout4-2026-11-13.json`, `r6-regression-holdout5-2026-11-13.json`.
- **Marks:** a script marked every test in this round (`score.py --auto`). No person has marked the round 6 set.

## The defect

The round 5 brief listed the backfill publisher cap under Open conflicts: 5k msg/s [PR 7] against 4k msg/s [Weekly 10-27]. The Decisions section of the same brief still said "Backfill publisher throttled to 5k msg/s [PR 7]". A person or an assistant that reads only Decisions acts on 5k.

No answer key tested this and no check covered it. The round 5 key asked only that the conflict was listed, so the test passed.

## The defect, reproduced first

The test came before the check ([b04d5da](https://github.com/eraserhead21/company-brain-poc/commit/b04d5da)). The round 5 brief and ledger are a fixture in `tests/fixtures/contested/`.

- Before the check existed: 8 failures and 1 error in 20 tests.
- After ([648a2fb](https://github.com/eraserhead21/company-brain-poc/commit/648a2fb)): 98 tests pass. The check fails the round 5 brief and names the line:
  `brief.md:23 (Decisions) states "Backfill publisher throttled to 5k msg/s" as settled, but it is one side of an open conflict`.
- The check also fails two older outputs with the same defect, with one failure each and no other line flagged: the two round 5 rebuilds, where the broker was an open conflict and Decisions gave Azure Event Hubs.

## What changed

1. **A check** in [`scripts/relations_check.py`](../scripts/relations_check.py). For each contradiction in the ledger, it reads every brief line outside Open conflicts and Sources. The line fails if it gives one side as a fact. The line passes if it says "contested".
   - A side with a number of its own: the line holds that number, and it cites that side's source or shares two words with the conflict.
   - A side with no number of its own: the line cites that side's source, holds one of the side's own words and shares two words with the item. Or the line holds every word of the claim.
2. **A rule for capture** ([`card-extractor.md`](../.claude/agents/card-extractor.md)):
   - Before: no rule. The brief had to list each contradiction under Open conflicts, and nothing covered the other sections.
   - After: "A contested value is never a settled fact. Each value in a `contradiction` is contested until a person decides. Go through every other section (Status, Key dates, Decisions, Open risks, Supersessions), line by line, old lines and new. If a line gives either value of a contradiction, whatever source the line cites, take the value out and write that the item is contested, with both sources ... Keep the parts of the line that no source disputes."
3. **A rule for the script marker** ([`tests/automark.py`](../tests/automark.py)): `not_settled`. No brief line outside Open conflicts matches the patterns, unless the line says "contested".

One change from the issue text. The issue asked for a check on lines that cite the same source as the ledger claim. The status update of 30 September also gives 5k, so a Decisions line that cites it passes that check with the defect in place. The check also fails a line from another source when the line shares two words with the conflict.

## Score

### The seen case: the round 5 output against the round 6 output

| Check | Round 5 output | Round 6 output |
|---|---|---|
| Relation check, contested values | 1 failure (0 before the check existed) | 0 failures in 14 relations |
| Backfill cap line under Decisions | "Backfill publisher throttled to 5k msg/s [PR 7]" | "Backfill publisher cap contested, see Open conflicts [PR 7] [Weekly 10-27]" |
| Main key | 20/20, 0 names, 12/12 | 20/20, 0 names, 12/12 |
| Round 4 key | 6/6, 0 names, 6/7 | 6/6, 0 names, 6/7 |
| Round 5 key (script) | 8/8, 0 names, 5/7 | 8/8, 0 names, 5/7 |

No existing score dropped.

### Unseen documents: round 5 rules against round 6 rules

- Built like rounds 4 and 5: the key ([813f64d](https://github.com/eraserhead21/company-brain-poc/commit/813f64d)) was written before the documents ([93a2198](https://github.com/eraserhead21/company-brain-poc/commit/93a2198)) and before any run saw them.
- 2 documents: a status update dated 5 November and weekly notes dated 10 November.
- Planted: 4 confidential details, 2 new names and 8 judgement tests. One of the 8 is the seen case from round 5.
- The control ran on a worktree of `main` at `e8320d1` with the same 2 documents. Its output is commit `c3f417b` on the branch `evals/contested-control`.

| Test | Control: round 5 rules | Round 6 rules |
|---|---|---|
| Redaction | 4/4 | 4/4 |
| Names leaked | 0 | 0 |
| **Judgement tests (script)** | **5/8** | **8/8** |
| Partition count, 12 against 32: listed as a conflict | fail | pass |
| Partition count: not given as settled | fail: Decisions keeps "12 partitions" | pass |
| Comparison window, local day against UTC day: listed as a conflict | pass | pass |
| Comparison window: not given as settled | pass, with a defect (see below) | pass |
| Backfill cap (seen case): not given as settled | fail: Decisions keeps 5k | pass |
| A conflict that a later document resolves (gate 0.2% corrected to 0.1%) | pass | pass |
| The same number about another item (a consumer at 5k msg/s) | pass | pass |
| The lesson | pass | pass |
| New relation check on the output | 1 failure | 0 failures |
| Cards written | 3 | 1 |
| Brief length | 576 words | 752 words |

What the new rules got right:

- **Three contested values left Decisions.** Each line now names the item and says "contested, see Open conflicts", with both sources.
- **A resolved conflict stayed settled.** The status update gave the go-live gate as 0.2%. The weekly notes said "0.1% daily mismatch, not 0.2%". The brief records the change under Supersessions and gives 0.1% with no "contested" mark.
- **The same number about another item stayed a fact.** "Consumer drained 5k msg/s" is under Status. Capture did not add it to the cap conflict, and the check did not flag it.

## What failed

- **The brief is 752 words. The limit is 600.** Each new conflict adds a quoted bullet, and each contested line cites two sources. Capture reported the length and left the cut to the caller. No script checks the length.
- **A part that no source disputes was lost.** The broker line was "Azure Event Hubs, Standard tier, 12 partitions keyed by meter_id". It is now "Azure Event Hubs, Standard tier. Partition count contested". The words "keyed by meter_id" are gone. The rule says to keep them.
- **The control hid a conflict in a card.** The control took the comparison window out of Decisions, which the script passed. It also wrote a card that gives the UTC day as the decision. The check reads the brief, not the cards. The run with the new rules wrote no such card, but no rule prevents it.
- **The control did not list the partition conflict.** Its report gave the cause: the decision record with the old value was not in the staged input. This is the same cause as the round 5 misses (claude-vault#140). The run with the new rules listed the conflict from the value in the brief line.

## Red team

Cases written to break the check, in [`tests/test_contested.py`](../tests/test_contested.py). The ones that held are tests. The ones that broke it are pinned as known-gap tests, which pass while the gap is open.

| Held | Broke it (pinned as a known gap) |
|---|---|
| The contested value cited from a third source | A contested value in a card |
| The same number about another item, from another document | The same number about another item, from the same source (PR 7 gives 5k twice) |
| A conflict that a later document resolves | A claim with no number, put in other words and cited from another document ("TL" for "Tech Lead") |
| A word value about another item ("UTC" in the storage decision) | |
| A claim that the brief line shortens (found on a round 5 rebuild, where the first version of the check missed it) | |
| A value that both sides share ("12 partitions" in a broker conflict) | |
| A line that names the item and gives no value | |

## New problems seen

- **The gate did not fire.** The new check runs inside capture. In this run it found 0 failures on the first pass, so the rule did the work. This round does not show capture fixing a contested line after the check fails it.
- **One run for each set of rules.** The difference between 5/8 and 8/8 is two runs of a model. A second run of either can differ.
- **A line with the value and the word "contested" passes.** The rule tells capture to take the value out. The check does not enforce that.
- **The script passes a deleted line.** `not_settled` passes when no line gives the value. A run that deletes the decision passes, as the control did for the comparison window.
- **The seen case is tuned.** The rule and the check were written with the backfill cap in view. The other 7 tests are unseen.

## Cost

- Run with the new rules: 95.6k Haiku tokens, 15 tool calls, 1m43s.
- Control run: 109.6k Haiku tokens, 18 tool calls, 2m28s.
- The check uses no tokens.

## Caveat

- The same person wrote the rules, the unseen documents and the key, as in rounds 4 and 5.
- No person has marked this round. In round 5 the script passed one test that a person failed.
- The extractor reports which files it opened. Nothing enforces the wall.
- Staged mode reads `sources/`, not Drive. The 2 unseen documents are not in the Drive folder.
