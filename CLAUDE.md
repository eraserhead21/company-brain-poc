# Company Brain POC: rules for this repo

This repo simulates one team project ("Project Alpha") and the org knowledge layer
on a single Claude Pro account. The design is summarised in README.md.

| Org piece | Stand-in here |
|---|---|
| OneDrive project folder | Google Drive folder `Claude Org POC/Project Alpha` |
| Teams channel | Drive doc `Team Channel Log` |
| Zoho Projects issues | GitHub Issues on this repo |
| Team GitHub repo | this repo: `src/`, `docs/`, `decisions/` |
| Org wiki | `learnings/approved/` |
| Enterprise search | claude.ai Project "Ask the Org" over `learnings/approved/` |

## Brief first

Answer questions about Project Alpha from `brief.md` and `learnings/approved/`
first. Open Drive files or GitHub only when those do not hold the answer, and
say that you did.

## Folders

- `brief.md`: the compiled project brief. Rewritten by `/capture`. Max 600 words.
  Line 3 holds `Compiled: <time>`. Every fact carries `[source]` inline.
- `log.md`: append-only run log. Holds the capture cursor. Never edit old lines.
- `learnings/approved/`: the org wiki. `/capture` writes new cards here **on a
  `capture/` branch** and opens a PR. Merging the PR is the approval. `main`
  never holds an unapproved card.
- `lint-report.md`: written by `/lint-wiki`.
- `poc-config.json`: Drive folder ID, repo name, and `drive_sources` (Drive
  title to `sources/` path).
- `sources/`: Markdown exports of the Drive docs, so citations resolve in the
  public repo. Capture reads Drive, not this folder, and cites these paths.
- `tests/answers/`: answer keys for the tests, published after the test rounds.
- `tests/results/`: one scored record per capture round (`score.py --save`).
- **Never read anything under `tests/` during capture or lint.** Reading it
  invalidates the tests.
- `iterations/`: one file per improvement round: score before, misses, rule
  change, score after, cost.

## Learning card format

File name: `learnings/approved/YYYY-MM-DD-<slug>.md`. One learning per card.

```
---
id: <YYYY-MM-DD-slug>
title: <one line>
type: learning | decision | risk
project: alpha
date: <YYYY-MM-DD of the event, not of capture>
owner_role: PM | TL | Engineer | Team
confidence: high | medium | low
sensitivity: internal
sources: [<sources/ path for a Drive doc, issue URL, PR URL or repo path>]
supersedes: <card id, or none>
---
**Context:** <one or two lines>
**What happened:** <one or two lines>
**What we learned:** <the reusable lesson, one or two lines>
```

## Redaction rules (apply before writing any card or the brief)

Never write any of these into a card, the brief or a PR description:

1. Names of people. Use roles: PM, TL, Engineer, customer contact.
2. Contact data: phone numbers, personal or customer email addresses, home addresses.
3. Health, leave, HR, performance or pay information.
4. Dates of birth or other personal identifiers.
5. Secrets: passwords, keys, tokens, VPN or Wi-Fi codes, credentials of any kind.
6. Customer identifiers: account numbers, household addresses.
7. Commercial terms: contract value, penalties, margins, disputes, vendor-switch talk.

If a learning cannot be written without one of these, drop the card and count it
in the run log as `dropped_confidential`.

## Conflicts

When two sources disagree and neither supersedes the other, do not pick one.
Write both claims into the brief's "Open conflicts" section, with their sources.
A later dated source that states a change ("moved to", "now", "replaces")
supersedes the earlier one. Record that as a supersession, not a conflict.

## Cost rules

- Extraction and linting run in Haiku subagents (`.claude/agents/`).
- Read only items changed since the cursor in `log.md`.
- Use `gh` for GitHub, not an MCP server.
