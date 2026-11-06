# Company Brain POC

A governed company brain turns project documents into redacted, approved knowledge that people and AI agents can query. For example, a lesson from cutover rehearsal notes becomes a learning card that any agent can cite, while a pay detail in the same folder never reaches a card.

Tested on project documents it had never seen, with its rules locked, it removed all 6 planted confidential values, leaked no names and passed 7 of 7 judgement checks. For more information, see [Results](#results).

## Overview

Project knowledge usually lives in meeting notes, chat, tickets and design docs. Nobody reads all of it, and nobody wants personal or commercial details from it spread across the company.

This proof of concept (POC) is a small working version of a fix. It runs two ways: as a Claude Code job on demand, or as n8n workflows (see [Operated with n8n](#operated-with-n8n)). The capture step reads one project's sources and writes two things:

- **A project brief:** one page of current status, decisions, risks, open conflicts and superseded facts. Every fact carries its source.
- **Learning cards:** short, reusable lessons ("request customer sandbox access at kickoff") that the rest of the company can search.

Nothing reaches the shared wiki until a person approves it. Personal data, secrets and commercial terms are removed before anyone sees the output. People and AI agents query only approved content: through a claude.ai Project, or through any MCP client connected to the n8n MCP server.

Built by Abhishek Katta with Claude Code and n8n. Portfolio: [abhishekkatta.netlify.app](https://abhishekkatta.netlify.app).

## Use cases

- Give AI agents project context they can cite, without exposing personal or commercial data.
- Reuse lessons across projects: a card written for one project answers the next team's question.
- Brief a new team member from one page instead of every meeting note.
- Show disagreements between sources instead of letting an agent pick one.

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
| Company search | A claude.ai Project whose only knowledge is the approved cards, or any MCP client through the n8n MCP server (W3) |

The design choices that matter:

- **Rules live in files, not in prompts.** [`CLAUDE.md`](CLAUDE.md) holds the card format, the 7 redaction rules and the conflict rule. The capture steps are in [`.claude/agents/card-extractor.md`](.claude/agents/card-extractor.md).
- **Cheap model, narrow job.** Extraction runs on Haiku and reads only items changed since a cursor kept in [`log.md`](log.md).
- **Disagreements are shown, not resolved.** When two sources disagree and neither replaces the other, the brief lists both under "Open conflicts". A later source that states a change is recorded as a supersession instead.
- **Approval is a merge.** Capture opens a PR. `main` never holds an unapproved card.

## Operated with n8n

The same capture and query flow also runs on n8n Cloud, with no Claude Code session. The workflow exports and an import guide are in [`n8n/`](n8n/).

- **W1 Capture:** a new Google Doc in the project folder goes to Claude Haiku with the redaction rules, then through the same regex backstop as [`scripts/redaction_check.py`](scripts/redaction_check.py). A clean card opens a PR. A doc that cannot be written without confidential detail is held and gets no card.
- **W2 Error alerts:** a production failure in W1, W3 or W3a sends an email with the failed node, the error and a link to the run.
- **W3 Ask the brain:** an MCP server behind a Bearer token, with two tools: `search_approved_cards` and `get_brief`. Both read only `main`, so an agent sees a card only after a person merges it.
- **W3a Card search:** the keyword search behind `search_approved_cards`. It returns up to 3 cards with their IDs, or "No approved learning covers this."

W1 writes cards only. The brief is still rebuilt by the Claude Code job.

### Prototype vs at scale

The gate does not change with size: an agent reads only what a person approved. What changes is how sources arrive, how text is checked and how cards are found.

| Step | In this prototype | At scale |
|---|---|---|
| Sources | One Drive folder, polled every minute. New docs only; edits to a doc are not captured. | Event triggers from Drive, SharePoint and Slack. An edited doc is captured again by revision. |
| Redaction | Rules in the Claude prompt, then a regex backstop. The model sees the raw text. | A PII and DLP service (Google Sensitive Data Protection, Microsoft Purview or Presidio) redacts before the model sees the text. The prompt rules and regex stay as extra layers. The model provider is on a zero-data-retention agreement. |
| Extraction | One card per doc, from the first 60,000 characters. JSON is parsed from the reply text. | Long docs split into chunks, several cards per doc, structured output checked against a schema. A new card is checked for duplicates against existing cards before its PR opens. The eval set runs again on every prompt change. |
| Held docs | The run stops at a no-op node. Nobody is told. | A review queue that records the reason and messages the doc owner. |
| Approval | One person merges a GitHub PR. | The same merge, with owners per topic (CODEOWNERS). n8n's send-and-wait approval in Slack or email for reviewers who do not use GitHub. |
| Retrieval | Keyword overlap. One GitHub call per card for each question. | Cards embedded on merge into a vector store (Qdrant or pgvector). Hybrid keyword and vector search. Answers still cite card IDs. |
| Freshness | Cards never expire. `/lint-wiki` flags stale claims when someone runs it. | Each card has an owner and a review-by date. Lint runs on a schedule, and a merged card that supersedes another retires it. |
| Access | One shared Bearer token. Every caller sees every approved card. | Per-user sign-in in front of the MCP endpoint. Results filtered by each card's `sensitivity` field. |
| Operations | An email on failure. One n8n Cloud trial account. | Retry On Fail on API nodes, Slack or on-call alerts, queue-mode workers, Git-backed dev and prod environments, external secrets. |
| Coverage and audit | Questions exist only in n8n's execution history. Nothing reports on them. | Every question is logged with the caller and the cards cited. Each "No approved learning covers this" is counted, and the count shows where the brain has gaps. |

For more information on what this prototype does not prove, see [Known gaps](#known-gaps).

## How it is tested

> [!NOTE]
> All project data in this repo is fictional. Names, contact details, secrets and commercial terms are planted for the redaction test.

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
| [`CLAUDE.md`](CLAUDE.md) | The rules: card format, redaction rules and the conflict rule |
| [`brief.md`](brief.md) | The current project brief |
| [`learnings/approved/`](learnings/approved/) | Approved learning cards |
| [`sources/`](sources/) | Exported copies of the Drive docs (fictional, with planted values) |
| [`src/`](src/), [`docs/`](docs/), [`decisions/`](decisions/) | The stand-in team repo: code, architecture notes and ADRs |
| [`iterations/`](iterations/) | One page per improvement round |
| [`tests/`](tests/) | Answer keys, scorer, saved results |
| [`scripts/redaction_check.py`](scripts/redaction_check.py) | Regex backstop for the redaction step |
| [`.claude/`](.claude/) | The capture and lint skills and their Haiku sub-agents |
| [`project-instructions/`](project-instructions/) | Instructions for the two claude.ai Projects |
| [`log.md`](log.md) | Append-only run log with counts, cost and the capture cursor |
| [`n8n/`](n8n/) | Exports of the four n8n workflows, with an import guide |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to run, review and extend the POC |
| [`poc-config.json`](poc-config.json) | Drive folder ID and the map from Drive doc titles to `sources/` files |

## Run it

You need Claude Code, the GitHub CLI, Python 3 and the Google Drive connector, plus your own Drive folder. Set its ID in [`poc-config.json`](poc-config.json).

> [!WARNING]
> Capture sends document text to the Anthropic API before redaction. Use test data only.

Use the following steps to run capture with Claude Code:

1. Run `/capture` in Claude Code in this folder. It opens a PR with new cards and a fresh brief.
2. Review the PR. Merge it to approve, or close it to reject.
3. Run `python tests/score.py`, then mark the judgement checks it prints. Add `--save <run>` to keep the record.
4. Run `/lint-wiki`. It writes [`lint-report.md`](lint-report.md): contradictions, stale claims, orphan cards and duplicates.
5. Optional: create the claude.ai Projects "Alpha" and "Ask the Org" from [`project-instructions/`](project-instructions/) to ask questions over the brief and the cards.

To run capture and queries on n8n instead, import the workflows in [`n8n/`](n8n/). For more information, see [`n8n/README.md`](n8n/README.md).
