# Company Brain POC

A company brain captures each team's learnings and shares them with the rest of the company, after a person approves them. People and AI assistants can then ask it questions.

![Project documents pass through redaction and a person's approval. Approved learning cards reach people and AI assistants; pay, phone numbers, passwords, and names never reach a card.](assets/company-brain-overview.svg)

For example, a team's meeting notes record that a test run of a new billing system found errors before go-live. These lessons become short learning cards that any AI assistant can quote. Sensitive information such as a colleague's pay, mentioned in the same folder, never reaches a card.

I tested my company brain on project documents it had never seen. It identified and removed all 6 fabricated confidential details, leaked no names, and passed 7 of 7 judgement tests that a person marked. For more information, see [Results](#results).

## Overview

Project knowledge sits in meeting notes, chat, tickets, and design documents. Nobody reads all of it, and nobody wants the personal or commercial details in it spread around the company.

This proof of concept (POC) reads one project's documents and writes two things:

- **A project brief:** One page with the current status, decisions, risks, points where documents disagree, and facts that later documents replaced. Each fact links to its source.
- **Learning cards:** Short lessons another team can reuse. For example, ask the customer for access to their test system during project kickoff.

> [!NOTE]
> Facts only reach the shared knowledge base after a person approves them; people and AI assistants can read only approved content. The capture job removes personal data, passwords, and commercial terms first.

The company brain has two modes of operation:

1. A Claude Code job that you run on demand.
2. Automated n8n workflows (see [Operated with n8n](#operated-with-n8n)).

Abhishek Katta built this with Claude Code and n8n. Portfolio: [abhishekkatta.netlify.app](https://abhishekkatta.netlify.app).

## Use cases

- **Retrieve sanitised knowledge:** AI assistants can quote project knowledge without exposing personal or commercial data.
- **Learn from other teams:** A person on one team can reuse another team's lessons without asking around.
- **Self-serve onboarding:** A new team member can query the knowledge base to get up to speed, saving productive hours for the team.
- **Transparent conflict-flagging:** Show conflicts between documents to a person, instead of letting an AI assistant make a decision.

## Why I built this

- **One GenAI setup:** To see how one Claude setup could serve both a project team and the whole company: shared context for the team, and a knowledge base anyone can ask questions.
- **Summarise once, read many:** Reading documents for every question is slow and expensive. I designed the brain to read only what changed since the last refresh, use a small, cheap AI model to pull out the facts, and answer from the brief before opening the original documents.
- **Eval set for trust:** I built evidence by hiding the failures a real company fears most in the test documents, such as leaked personal data, made-up facts, and conflicts settled without anyone noticing. I then scored each iteration.

## How it works

![Five steps: collect documents, draft cards with Claude Haiku, redact confidential details, a person approves the pull request, then people and AI assistants ask questions.](assets/how-it-works.svg)

The capture job opens a pull request (PR) on GitHub to propose a change for review. A person accepts this change by merging the PR.

This prototype uses simple stand-ins for company systems, such as a Google Drive folder for the project file share. To see every stand-in and how each part changes at scale, see [Prototype vs at scale](#prototype-vs-at-scale).

## Key design choices

- **Rules in files instead of prompts.** See [`CLAUDE.md`](CLAUDE.md) for the card format, the 7 redaction rules (what to remove), and the conflict rule. See the capture steps in [`.claude/agents/card-extractor.md`](.claude/agents/card-extractor.md).
- **Small model, narrow job.** Claude Haiku, a small and cheap model, pulls out the facts. It reads only what changed since the last run. [`log.md`](log.md) records where the last run stopped.
- **Show conflicts, do not resolve them.** When two documents disagree and neither replaces the other, the brief lists both under "Open conflicts". When a later document clearly states a change, the brief records the new fact and marks the old one as replaced.
- **Approval is a merge.** Capture opens a pull request. The `main` branch, the approved version, never holds an unapproved card.

## Operated with n8n

n8n is a workflow automation tool. The same capture and question-answering steps also run as four n8n workflows, with no Claude Code session. See [`n8n/`](n8n/) for the workflow exports and an import guide.

- **W1 Capture:** When a new Google Doc appears in the project folder, n8n sends it to Claude Haiku with the redaction rules, then runs the same pattern check as [`scripts/redaction_check.py`](scripts/redaction_check.py). A clean card then opens a pull request. If Claude cannot write the lesson without confidential details, W1 holds the document and writes no card.
- **W3 Ask the brain:** W3 runs a Model Context Protocol (MCP) server that offers two tools: `search_approved_cards` and `get_brief`. A secret access key (a Bearer token) protects it. Both tools read only the approved version on the `main` GitHub branch, so an assistant sees only person-reviewed cards.
- **W3a Card search:** The keyword search powering `search_approved_cards`. It returns up to 3 cards with their IDs, or "No approved learning covers this."
- **W2 Error alerts:** If W1, W3, or W3a fails during a real run, n8n sends the failed step, the error, and a link to the failed run to a support email address.

> [!NOTE]
> - MCP is the standard way AI assistants connect to outside tools.
> - W1 only writes cards. The Claude Code job still rebuilds the brief.

## Prototype vs at scale

The prototype runs on stand-ins for company systems: a Drive folder for the file share, GitHub for the issue tracker and the knowledge base, and a claude.ai Project or W3 for company search. The table lists each stand-in under the part it serves.

The approval step stays the same at any scale: an AI assistant reads only what a person approved. What changes is how documents come in, how the system catches confidential details, and how people find cards.

<details>
<summary>Show all 10 parts and how each one changes at scale</summary>

| Step | In this prototype | At scale |
|---|---|---|
| Sources | Stand-ins: a Google Drive folder for the project file share (copies in [`sources/`](sources/)), a Drive document holding a chat log for team chat, GitHub Issues on this repo for the issue tracker, and this repo ([`src/`](src/), [`docs/`](docs/), [`decisions/`](decisions/)) for team code and design records.<br>n8n checks the Drive folder every minute. It picks up new documents only, not edits. | Drive, SharePoint, and Slack notify the system as soon as something changes. The system captures an edited document again. |
| Redaction | Rules in the instructions to Claude, then a pattern check. Claude sees the original text. | A dedicated tool for finding personal and sensitive data (such as Google Sensitive Data Protection, Microsoft Purview, or Presidio) removes it before Claude sees the text. The rules and the pattern check stay as extra layers. The AI provider agrees not to store the data. |
| Extraction | One card per document, from the first 60,000 characters. | The system splits long documents into parts, writes several cards per document, and checks every card against a fixed format. It compares each new card with existing cards to avoid duplicates. The test set runs again whenever the instructions change. |
| Held documents | The workflow stops and tells nobody. | A review list records why W1 held the document and tells its owner. |
| Approval | One person merges a pull request on GitHub. | The same merge, with a named owner for each topic. Reviewers who do not use GitHub approve in Slack or email, through n8n's built-in approval step. |
| Search | Stand-ins: [`learnings/approved/`](learnings/approved/) for the company knowledge base. For company search, a claude.ai Project (a Claude workspace limited to chosen files) that knows only the approved cards, or any AI assistant connected through the n8n workflow W3.<br>Simple keyword matching. Each question reads every card from GitHub. | The system indexes cards when a person approves them, so search can match meaning as well as keywords ("leave" also finds "absence"). Answers still cite card IDs. |
| Freshness | Cards never expire. The check for out-of-date claims (`/lint-wiki`) runs only when someone starts it. | Each card has an owner and a review date. The check runs on a schedule, and a newer card retires the one it replaces. |
| Access | One shared access key. Everyone with the key sees every approved card. | Each person signs in and sees only the cards their role allows, using each card's `sensitivity` field. |
| Operations | An email when a workflow fails. One n8n trial account. | Automatic retries, alerts in Slack or to the on-call person, extra capacity for busy periods, separate test and live setups, and keys in a secure vault. |
| Coverage and audit | Only n8n's run history stores questions. Nobody reviews them. | The system logs every question with who asked and which cards answered. It counts each "No approved learning covers this", which shows what the brain is missing. |

</details>

For more information on what this prototype does not prove, see [Known gaps](#known-gaps).

## How I tested it

> [!NOTE]
> All project data in this repo is fictional. I fabricated the names, contact details, passwords, and commercial terms.

"Project Alpha" is the test project: a utility company moving its smart-meter readings to a new real-time billing system. Its documents contain confidential information that the capture job must handle:

- **Redaction:** 11 people's names, and 20 fabricated confidential details (phone number, home address, health, pay, performance, date of birth, passwords, access tokens, customer account, contract value, profit margin, talk of switching suppliers, and an invoice dispute).
- **Judgement:** 3 places where documents show conflicting information, 1 fact that a later document replaced, and 8 lessons a careful reader would find.
- **Answer key:** [`tests/answers/`](tests/answers/). The rules tell the capture job never to read `tests/`.
- **Unseen test set:** 2 more Drive documents and 1 issue with new kinds of hidden details, an answer key that I wrote before any run saw them, and one trap (the same date written two ways).

[`tests/score.py`](tests/score.py) checks redaction and names automatically, and lists the judgement tests for a person to mark. [`tests/results/`](tests/results/) holds each round's marks and scores.

## Results

| Round | Change | Redaction | Names leaked | Judgement tests |
|---|---|---|---|---|
| 1 | First version | 20/20 | 0 | 8/12 |
| 2 | New rules for conflicts and lessons | 20/20 | 0 | 11/12 |
| 3 | Clearer wording for conflicts, after reviewer feedback | 20/20 | 0 | 11/12, less clutter |
| 4 | **Unseen documents, rules locked** | **6/6** | **0** | **7/7** |

Each round has a page in [`iterations/`](iterations/) with failures, the exact rule change, the score after, and the cost. Round 3 is the clearest example: a reviewer said the list of conflicts was unclear, and the page shows the list before and after the rule change.

## Known gaps

- **The brief still misses one conflict in the main test set (C1).** C1 is not in the unseen set, which is why round 4 shows 7/7. A meeting note says "Agreed: retention is 30 days"; the design document says 90. The rule reads "agreed" as a change, so the brief treats 30 days as the new fact instead of flagging the conflict.
- **No test scores made-up facts.** Round 1 made up 4 facts. A human review missed one of them, and a user's query on a Claude Project repeated this fact with confidence. A spot check of the current output found no unsourced numbers or reasons, but no script tests for this yet.
- **Redaction protects the knowledge base, not the original documents.** A Project that read the Drive documents directly answered one question with a team member's leave dates. The company brain needs controls for access to the original documents.

<details>
<summary>Show 6 more gaps</summary>

- **The one-page brief loses history.** The 600-word limit pushed older, replaced dates out of the brief in round 4. The cards still hold this information.
- **I tuned rounds 2 and 3 on the same test I scored them on.** Round 4 is the only unseen test, and the same person wrote its documents and the rules.
- **A person, not a script, marks the judgement tests.**
- **Cost doubled** from round 1 to round 2 as the rules grew: from about 59,000 to 115,000 Haiku tokens for a full rebuild, and 93,000 for a small update.
- **I have not run the cost test yet.** [`tests/eval_questions.md`](tests/eval_questions.md) compares answering from the brief with answering from the original documents.
- **One-person simulation.** No real user roles, single sign-on, permission-aware search, Microsoft 365, or ticketing system. The stand-ins show the shape of the solution, not how it behaves at scale.

</details>

## Repo map

<details>
<summary>Show what each file and folder holds</summary>

| Path | Description |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | The rules: card format, what to remove, and how to handle conflicts |
| [`brief.md`](brief.md) | The current project brief |
| [`learnings/approved/`](learnings/approved/) | Approved learning cards |
| [`sources/`](sources/) | Copies of the Drive documents (fictional, with planted details) |
| [`src/`](src/), [`docs/`](docs/), [`decisions/`](decisions/) | The stand-in team repo: code, architecture notes, and architecture decision records (ADRs) |
| [`iterations/`](iterations/) | One page per improvement round |
| [`tests/`](tests/) | Answer keys, the scoring script, and saved results |
| [`scripts/redaction_check.py`](scripts/redaction_check.py) | The pattern check that backs up the redaction step |
| [`.claude/`](.claude/) | The Claude Code commands for capture and checking, and the small-model helpers they use |
| [`project-instructions/`](project-instructions/) | Instructions for the two claude.ai Projects |
| [`log.md`](log.md) | A log of every run: counts, cost, and where the last run stopped |
| [`n8n/`](n8n/) | Exports of the four n8n workflows, with an import guide |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to run, review, and extend the POC |
| [`poc-config.json`](poc-config.json) | The Drive folder ID, and which Drive document matches which file in `sources/` |

</details>

## Run it

You need Claude Code, the GitHub CLI, Python 3, and the Google Drive connector, plus your own Drive folder. Set its ID in [`poc-config.json`](poc-config.json).

> [!WARNING]
> Capture sends document text to the Anthropic API before redaction. Use test data only.

<details>
<summary>Show the steps to run capture with Claude Code</summary>

1. Run `/capture` in Claude Code in this folder. It opens a pull request with new cards and a fresh brief.
2. Review the pull request. Merge it to approve, or close it to reject.
3. Run `python tests/score.py`, then mark the judgement tests it prints. Add `--save <run>` to keep the record.
4. Run `/lint-wiki`. It writes [`lint-report.md`](lint-report.md): conflicts, out-of-date claims, unlinked cards, and duplicates.
5. Optional: create the claude.ai Projects "Alpha" and "Ask the Org" from [`project-instructions/`](project-instructions/) to ask questions over the brief and the cards.

</details>

To run capture and questions on n8n instead, import the workflows in [`n8n/`](n8n/). For more information, see [`n8n/README.md`](n8n/README.md).
