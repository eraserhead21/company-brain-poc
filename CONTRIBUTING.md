# Contributing

This POC is small on purpose. Every change goes through a pull request, and `main` holds only what a person approved.

## How a doc becomes a card

There are two ways to run capture. Both end in a pull request.

- **Claude Code:** run `/capture` in this folder. It reads what changed since the cursor in [`log.md`](log.md), writes cards and rebuilds [`brief.md`](brief.md). See [Run it](README.md#run-it).
- **n8n:** add a Google Doc to the project folder. W1 writes one card and opens a PR on a `capture/n8n-<timestamp>` branch. See [Operated with n8n](README.md#operated-with-n8n).

## Review

- **Merge** the PR to approve the card. Agents can read it from that moment.
- **Close** the PR to reject it.
- To fix a card, edit the file on the PR branch, then merge.

Check every card against the redaction rules in [`CLAUDE.md`](CLAUDE.md) before you merge. The regex backstop catches patterns, not meaning.

## Held docs

A held doc gets no card and no PR. In n8n, W1 holds a doc for one of three reasons:

- `dropped_confidential`: the lesson cannot be written without personal, secret or commercial detail.
- `redaction backstop hit`: the card passed Claude but failed the regex check.
- Not a learning: for example, a status update that only restates the plan.

The held doc stays in Drive. Nothing about it reaches `main`.

## Tests

```bash
python tests/score.py
```

A passing run prints `caught 20/20` for redaction and `0 name(s) leaked`. It then lists the judgement checks for a person to mark. Add `--save <run>` to keep the record in [`tests/results/`](tests/results/).

Run it after any change to the rules, the prompts or the cards.

## Sources

Everything in [`sources/`](sources/) is fictional. The names, contact details, secrets and commercial terms are planted for the redaction test, so do not scrub them, and never add real data. A new source needs the export header used by the other files, and new planted values need matching entries in [`tests/answers/`](tests/answers/).

## Workflows

To change an n8n workflow, edit it in n8n, export it, remove credential IDs and personal data, and replace the file in [`n8n/`](n8n/). See [`n8n/README.md`](n8n/README.md) for the placeholders.
