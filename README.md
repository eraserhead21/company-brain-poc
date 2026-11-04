# Company Brain POC

**Held-out result, rules frozen:** 6/6 planted confidential values removed, 0 names leaked, 7/7 judgement checks. See [Results](#results).

Project knowledge usually lives in meeting notes, chat, tickets and design docs. Nobody reads all of it, and nobody wants personal or commercial details from it spread across the company.

This POC is a small working version of a fix. A Claude Code job, run on demand, reads one project's sources and writes two things:

- **A project brief:** one page of current status, decisions, risks, open conflicts and superseded facts. Every fact carries its source.
- **Learning cards:** short, reusable lessons ("request customer sandbox access at kickoff") that the rest of the company can search.

Nothing reaches the shared wiki until a person approves it. Personal data, secrets and commercial terms are removed before anyone sees the output.

Built by Abhishek Katta with Claude Code, on a single Claude Pro account. Portfolio: [abhishekkatta.netlify.app](https://abhishekkatta.netlify.app).

## Why I built this

- The question was how one Claude setup could serve a real project team and the wider organisation: team-level shared context, plus an org-wide knowledge system anyone can query.
- The first design read every source on every question. That is expensive, so the design became "summarise once, read many": read only what changed, extract with a small model, and answer from the brief before opening raw sources.
- Before trusting it, I wanted evidence. So the POC plants the failure modes a real rollout fears most (leaked personal data, silently settled disagreements, invented facts) and scores every run.

## How it works

```text
Project sources                     Capture job                      Human gate            Company
(Drive docs, GitHub issues,  --->   Haiku sub-agent reads only  --->  Pull request:  --->  Wiki of approved
 PRs, ADRs, code)                   what changed since the last       merge = approve      cards, searchable
                                    run, redacts, writes cards                             through a claude.ai
                                    and the brief; a regex check                           Project
                                    runs as a backstop
```

| Org piece | Stand-in here |
|---|---|
| Project file share | Google Drive folder (exported copies in [`sources/`](sources/)) |
| Team chat | A Drive doc holding a channel log |
| Issue tracker | GitHub Issues on this repo |
| Team repo | This repo: [`src/`](src/), [`docs/`](docs/), [`decisions/`](decisions/) |
| Company wiki | [`learnings/approved/`](learnings/approved/) |
| Company search | A claude.ai Project whose only knowledge is the approved cards |

The design choices that matter:

- **Rules live in files, not in prompts.** [`CLAUDE.md`](CLAUDE.md) holds the card format, the 7 redaction rules and the conflict rule. The capture steps are in [`.claude/agents/card-extractor.md`](.claude/agents/card-extractor.md).
- **Cheap model, narrow job.** Extraction runs on Haiku and reads only items changed since a cursor kept in [`log.md`](log.md).
- **Disagreements are shown, not resolved.** When two sources disagree and neither replaces the other, the brief lists both under "Open conflicts". A later source that states a change is recorded as a supersession instead.
- **Approval is a merge.** Capture opens a PR. `main` never holds an unapproved card.

## How it is tested

The project is fictional ("Project Alpha", a smart-meter streaming migration). Its sources are seeded with things the job must handle:

- **Redaction:** 20 planted confidential values (phone, home address, health, pay, performance, date of birth, passwords, tokens, customer account, contract value, margin, vendor-switch talk, invoice dispute) and 11 people's names.
- **Judgement:** 3 conflicts between sources, 1 supersession and 8 lessons a good reader should find.
- **Answer key:** [`tests/answers/`](tests/answers/). The capture job is told never to read `tests/`.
- **Held-out set:** 2 more Drive docs and 1 issue with new kinds of planted values, a separate answer key written before any run saw them, and one trap (the same date written two ways).

[`tests/score.py`](tests/score.py) checks redaction and names automatically and lists the judgement checks for a person to mark. Each round's marks and scores are saved in [`tests/results/`](tests/results/).

## Results

| Round | Change | Redaction | Names leaked | Judgement checks |
|---|---|---|---|---|
| 1 | Baseline | 20/20 | 0 | 8/12 |
| 2 | Conflict and lesson rules | 20/20 | 0 | 11/12 |
| 3 | Conflict wording, after reviewer feedback | 20/20 | 0 | 11/12, noise removed |
| 4 | **Held-out set, rules frozen** | **6/6** | **0** | **7/7** |

Each round has a page in [`iterations/`](iterations/) with what failed, the exact rule change, the score after and the cost. Round 3 is the clearest example: a reviewer said the conflict list was unclear, and the page shows the list before and after the rule change.

## Known gaps

- **One conflict in the main test set is still missed (C1).** C1 is not in the held-out set, which is why round 4 shows 7/7. A meeting note says "Agreed: retention is 30 days"; the design doc says 90. The rule reads "agreed" as a change, so the brief records a supersession where the key expects an open conflict.
- **Invented facts are not scored.** Round 1 invented 4 facts; one passed human review, and the query Project then repeated it with confidence. A spot check of the current output found no unsourced numbers or reasons, but no script tests this yet.
- **Redaction protects the wiki, not the raw sources.** A Project that reads the Drive docs directly answered one question with a team member's leave dates. Query access to raw sources needs its own controls.
- **The one-page brief loses history.** The 600-word cap pushed older superseded dates out of the brief in round 4. The cards still hold them.
- **Rounds 2 and 3 were tuned against the test they are scored on.** Round 4 is the only held-out result, and its documents were written by the same person who wrote the rules.
- **Judgement checks are marked by a person,** not by a script.
- **Cost doubled** from round 1 to round 2 as the rules grew (about 59k to 115k Haiku tokens for a full rebuild; 93k for a small delta).
- **The cost test is not run yet.** [`tests/eval_questions.md`](tests/eval_questions.md) compares answering from the brief with answering from raw sources.
- **Single-user simulation.** No real roles, SSO, permission-aware search, Microsoft 365 or ticketing system. The stand-ins above show the shape, not the scale.

## Repo map

| Path | What it is |
|---|---|
| [`brief.md`](brief.md) | The current project brief |
| [`learnings/approved/`](learnings/approved/) | Approved learning cards |
| [`sources/`](sources/) | Exported copies of the Drive docs (fictional, with planted values) |
| [`iterations/`](iterations/) | One page per improvement round |
| [`tests/`](tests/) | Answer keys, scorer, saved results |
| [`scripts/redaction_check.py`](scripts/redaction_check.py) | Regex backstop for the redaction step |
| [`.claude/`](.claude/) | The capture and lint skills and their Haiku sub-agents |
| [`project-instructions/`](project-instructions/) | Instructions for the two claude.ai Projects |
| [`log.md`](log.md) | Append-only run log with counts, cost and the capture cursor |

## Run it

Needs Claude Code, the GitHub CLI, Python 3 and the Google Drive connector, plus your own Drive folder (set its id in [`poc-config.json`](poc-config.json)).

1. `/capture` in Claude Code in this folder. It opens a PR with new cards and a fresh brief.
2. Review the PR. Merge it to approve; close it to reject.
3. `python tests/score.py`, then mark the judgement checks it prints. Add `--save <run>` to keep the record.
4. `/lint-wiki` writes [`lint-report.md`](lint-report.md): contradictions, stale claims, orphan cards, duplicates.
5. Optional: create the claude.ai Projects "Alpha" and "Ask the Org" from [`project-instructions/`](project-instructions/) to ask questions over the brief and the cards.
