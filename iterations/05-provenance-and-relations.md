# Round 5: provenance check, typed relations, script-marked tests

- **Date:** 2026-11-12
- **Question:** can the brain check its own facts against its sources, type each conflict on purpose, and prove both with scripts?
- **Runs:** two full rebuilds from all sources, then one delta run on 3 unseen documents. All three in staged mode (see below). See `log.md`.
- **Rules:** [8616e88](https://github.com/eraserhead21/company-brain-poc/commit/8616e88), frozen before the unseen documents were added.
- **Score records:** `tests/results/r5-rebuild-1-2026-11-12.json`, `r5-rebuild-2026-11-12.json`, `r5-rebuild-holdout4-2026-11-12.json`, `r5-holdout-2026-11-12.json`, `r5-regression-2026-11-12.json`, `r5-regression-holdout4-2026-11-12.json`.
- **Marks:** a script marked the rebuild (`score.py --auto`). A person marked the unseen set on 2026-11-13: `tests/results/r5-holdout-2026-11-12.marks.txt`. No person has marked the rebuild.

## What changed

1. **Provenance check** ([`scripts/provenance_check.py`](../scripts/provenance_check.py)). For each card and each fact line in the brief, every number with its unit, date, time, version, identifier and quantity word must be in a source that the card or line cites. A citation must resolve to a file under the source folders. The check stores pointers (file and line), never source text. It has no model.
2. **Typed relations** ([`scripts/relations_check.py`](../scripts/relations_check.py), [`relations.json`](../relations.json)). Capture records each disagreement as a contradiction, a supersession or a scope difference. The check looks for the evidence in the later source itself. It does not trust the ledger.
   - Before: "A later source that states a change ("moved to", "now", "replaces", "agreed") is a supersession."
   - After: a supersession needs a later-dated source that gives the old value after a cue ("was 14 November", "not 5"), or has a change word in the sentence with the new value, or names the document it replaces. "A decision word alone ("agreed", "decided", "confirmed", "approved") is not evidence of a change."
3. **Script-marked judgement tests** ([`tests/automark.py`](../tests/automark.py)). Each test in an answer key carries a match rule. `score.py --auto` marks the tests from the brief, the cards and the ledger.
4. **Gate inside capture.** The extractor runs the redaction, provenance and relation checks on its own output and gets up to 2 fix passes. [`scripts/run_checks.py`](../scripts/run_checks.py) runs every check with one command.
5. **Staged mode** ([`scripts/stage_sources.py`](../scripts/stage_sources.py)). Capture can read header-stripped copies of `sources/` in place of Drive and GitHub. This round used it, so no document went into the live Drive folder and no live n8n workflow ran.
6. **A tighter wall.** The extractor must not open `iterations/`, `README.md`, `n8n/` or any line of `log.md` except the last. Before this round, `log.md` and the README both described the C1 answer, and capture read `log.md` for its cursor.

## The C1 miss, reproduced first

- `score.py --auto` on the round 4 output: C1 fails, "no bullet under Open conflicts holds both claims". 11/12, the same as the saved human mark.
- `relations_check.py` on the pair that round 4 recorded as a supersession (90 days to 30 days): fails, "no evidence of a change ... Line 14 has a decision word ("Agreed"), which is not evidence on its own."
- Both tests are in `tests/test_relations.py`, class `C1Reproduction`.

## Score

Same key, before and after. "Round 4" is the output on `main`. "Round 5" is rebuild attempt 2.

| Check | Round 4 | Round 5 rebuild |
|---|---|---|
| Redaction, main key | 20/20 | 20/20 |
| Names leaked | 0 | 0 |
| Judgement tests, main key | 11/12 (person and script agree) | 12/12 (script) |
| Redaction, round 4 key | 6/6 | 6/6 |
| Names leaked, round 4 key | 0 | 0 |
| Judgement tests, round 4 key | 7/7 (person and script agree) | 7/7 (script) |
| Provenance failures | 3 in 109 checked items | 0 in 102 |
| Relation failures | no ledger | 0 in 10 relations |

- C1 is now an open conflict: 90 days [Design v1] versus 30 days [Weekly 09-29].
- The 3 provenance failures on round 4 are 2 problems. One card gives a date and a version from a document it does not cite. One card says "one hour" where the source gives "02:00 to 03:00".

### Unseen documents (round 5 held-out set)

- Built like round 4: the key (`tests/answers/holdout5.json`) was written before the documents were added and before any run saw them.
- 3 documents: design review notes dated 12 September, weekly notes dated 27 October, and ADR-003.
- Planted: 8 confidential details written to avoid the pattern check (pay in words, health with no keyword, a token with no colon, a vendor switch as a paraphrase, an account number with no prefix, a date of birth in two forms), 2 new names with one written as an initial and a surname, and 7 judgement tests.

| Check | Result |
|---|---|
| Redaction | 8/8 |
| Names leaked | 0 |
| Judgement tests | **4/7** (person). The script marked 5/7 |
| Main key after the delta run | 20/20, 0 names, 12/12 (script) |
| Round 4 key after the delta run | 6/6, 0 names, 6/7 (script) |

What it got right:

- **Decision word alone.** "Confirmed: the backfill publisher cap is 4k msg/s" against 5k in PR 7: listed as an open conflict.
- **A record that names what it replaces.** ADR-003 "replaces section 2 (Message broker) of Solution Design v1": the broker moved from Open conflicts to a supersession.
- **One date written two ways.** "2026-11-19" and "19 November": not listed as a conflict.
- **The lesson** became a card: ask for the meter-group rollout order together with the firmware date.

## What failed

- **Rebuild attempt 1 lost two lessons.** It fixed C1 but wrote 9 cards and no card for the kickoff access lesson (L4) or the firmware risk (L6): 10/12. Fix: one rule, "Go through the sources one at a time ... A risk in a risk register or an open issue is a risk card" ([8616e88](https://github.com/eraserhead21/company-brain-poc/commit/8616e88)). Attempt 2 wrote 12 cards and scored 12/12. This fix was tuned on the scored set, like rounds 2 and 3.
- **Unseen set, partition count.** Review notes dated 12 September say "moved to 24". ADR-002, dated 24 September, says 12. Capture did not make 24 the current value, which is correct. It also did not list the conflict. Its report gave the cause: a delta run reads only the new documents, and it would not record a relation against a document it had not read in that run.
- **Unseen set, shadow run length.** "Agreed: the shadow run is 9 days, up from 7." A card records 7 to 9 days and Key dates shows 9 days. The ledger and the Supersessions section do not hold the change. The script passed this test. The person failed it.
- **Unseen set, scope difference.** A dry-run alert at 0.5% per day and the go-live gate at 0.1% per day are two scopes. Capture recorded nothing. No run in this round wrote a scope relation, so only unit tests cover that type.
- **Round 4 key after the delta run: HS2 fails by script.** The new weekly notes say the firmware rollout finished, so the brief dropped the "27 October" line from Key dates. The date is still under Supersessions. The script rule wants it stated outside that section. The round 4 key was written for the round 4 sources.

## Red team

Cases written to break each part. The ones that held are now tests. The ones that broke it are pinned as known-gap tests, which pass while the gap is open.

| Part | Held | Broke it (pinned as a known gap) |
|---|---|---|
| Provenance | A citation into `tests/`, a path that climbs out, an issue in another repo, a missing file, a wrong unit ("15 weeks"), a fact from an uncited document, a source edited after approval, a section number used as support | A negation ("No duplicates" to "Duplicates were seen"), a wrong number that the source also holds, an invented reason with no number |
| Relations | "was" in the next sentence, a change word about another value in the same line, the old value named with no cue, an older document replacing a newer one, a document with no date, the same pair typed twice, a real supersession typed as a conflict, text that is not JSON | Two values about different topics joined by a change word |
| Script marks | Conflict words spread over two bullets, a conflict named only in a card, a conflict in the ledger that the brief hides, listing everything as a conflict | None pinned. See the two limits under New problems seen |
| Pattern check for redaction | A phone in local format, a date of birth in words and in ISO form | Pay in words, health with no keyword, a token with no colon, a vendor switch as a paraphrase, an account number with no prefix, a name as initial and surname |

- **Round 1 inventions as known-bad cases.** The text of all 4 comes from git history. The check fails 3 of the 4: "about 6 weeks", "same-day", and a backfill end date with no source. The 4th is an invented reason ("log retention policy"). The check lists "policy" for review and does not fail it.
- **Mutation test.** One number, date or version made wrong in each card line, and each card's sources swapped: the check catches 80 of 87. In each of the 7 it misses, the wrong value is also in a cited source.
- **The gate, in the run.** In rebuild attempt 2 the extractor's first check run had 4 failures. 3 were real and it fixed them: "double" for a 2.3% rise, and a version and a date from a document the brief line did not cite. 1 was a fault in the check (a "None." bullet), fixed after the round.

## New problems seen

- **The checks pass an output that misses a relation.** All three checks reported 0 failures on the unseen run that scored 4/7. They test what capture wrote. They cannot find what it left out.
- **A script mark is cruder than a person.** The first rule set agreed with 54 of the 55 saved human marks. It missed "3 times" for "3x". After that one rule change it agrees with 55 of 55. The rules were written with those marks in view. On the unseen set it agrees with 6 of 7: it passed the shadow run length test, and the person failed it.
- **A contested value stated as a decision.** The brief lists the backfill cap under Open conflicts (5k against 4k) and still gives 5k under Decisions. The key does not test this, so the test passed. The person who marked the set found it. Issue: claude-vault#139.
- **A role slip.** One card says "the vendor" where the source means the customer. The provenance check cannot see this.
- **A full rebuild renames cards.** 3 of the 13 card IDs on `main` are still there after the rebuild. An eval case that names a card ID can break.
- **n8n W1 cards cite "Google Drive: <title>".** The check now maps that to the export in `sources/`. A W1 card for a document with no export fails the check.
- **The supersession in a card, not in the ledger.** For "9 days, up from 7" the delta run wrote a card but no relation, because the document with the old value was not in that run.

## Cost

- Rebuild attempt 1: 115.2k Haiku tokens, 47 tool calls, 2m36s.
- Rebuild attempt 2: 123.5k Haiku tokens, 51 tool calls, 3m22s (round 3 rebuild: 105.2k). This round read 14 documents and 8 GitHub snapshots. Round 3 read 10 documents. The two numbers do not compare one to one.
- Delta run on 3 documents: 95.5k Haiku tokens, 16 tool calls, 1m45s (round 4 delta: 92.8k).
- The three check scripts use no tokens.

## Caveat

- The same person wrote the rules, the unseen documents and the key, as in round 4.
- The extractor reports which files it opened. Nothing enforces the wall.
- Staged mode reads `sources/`, not Drive. The 3 unseen documents are not in the Drive folder.
- The check scripts changed twice after the unseen run, for the two faults named above and for section numbers. No extractor rule changed after the freeze.
