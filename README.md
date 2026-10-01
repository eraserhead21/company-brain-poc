# Claude Org POC

A one-person simulation of the org design at
https://claude.ai/artifact/UfRHRySzJNREd3tTwyD25s, on Claude Pro.
Rules for Claude live in `CLAUDE.md`.

## What runs where

| Piece | Where | Proves |
|---|---|---|
| Project files (9 docs) | Google Drive `Claude Org POC/Project Alpha` | Layer 2 sources |
| Code, ADRs, Issues, PRs | this repo on GitHub | Layer 2 sources, Zoho stand-in |
| `/capture` skill + `card-extractor` (Haiku) | Claude Code in this repo | Layer 3 capture, cost rules |
| Capture PR, merge = approve | GitHub | Layer 3 review gate |
| `/lint-wiki` skill + `wiki-linter` (Haiku) | Claude Code | Layer 3 upkeep |
| Project "Alpha" | claude.ai | Layer 2 team workspace, brief-first |
| Project "Ask the Org" | claude.ai | Enterprise search stand-in |
| `tests/` | local | Redaction, conflicts, cost |

## Runbook

### One time, by hand in claude.ai
1. Create Project **Alpha**. Paste `project-instructions/alpha-project.md` into
   Instructions. Add knowledge: Google Drive > the 9 files in `Project Alpha`;
   GitHub > this repo, files `brief.md` and folder `learnings/approved/`.
2. Create Project **Ask the Org**. Paste `project-instructions/ask-the-org.md`.
   Add knowledge: GitHub > this repo, folder `learnings/approved/` only.

### Each cycle, in Claude Code (VS Code) in this folder
1. `/capture`: opens a PR with new cards and a fresh brief.
2. Review the PR on GitHub. Merge it to approve. Close it to reject.
3. `git pull`, then `python tests/score.py`: redaction and name leaks.
   Use the full Python path on this machine.
4. `/lint-wiki`: writes `lint-report.md`.
5. In claude.ai, click **Sync now** on both Projects.

### Tests
- **Delta test:** after the first capture, add one new doc to the Drive folder
  and run `/capture` again. Pass: the PR body shows `drive_files_read: 1`.
- **Redaction test:** `tests/score.py`. Pass: 20/20 caught, 0 names.
- **Conflict test:** tick C1 to C3 and S1 printed by `tests/score.py` against
  `brief.md`. Pass: 3/3 conflicts flagged, S1 recorded as a supersession.
- **Lint test:** `/lint-wiki`. Pass: every conflict the brief missed shows up.
- **Cost test:** `tests/eval_questions.md`.
- **Haiku test:** re-run one capture with the subagent set to `model: sonnet`
  on a throwaway branch, and compare the cards.

## Not simulated here
Multi-user roles, Teams, Zoho, OneDrive sync, SSO/SCIM, enterprise search
permissions, org spend caps. See the "Cannot simulate" table in the plan.
