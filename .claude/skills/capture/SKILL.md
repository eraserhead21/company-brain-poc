---
name: capture
description: Run the Project Alpha capture job. Reads only sources changed since the last run (Drive folder, GitHub issues, PRs, repo docs) through the Haiku card-extractor subagent, writes redacted learning cards, the relation ledger and a fresh brief.md on a capture branch, runs the checks, then opens a PR for human approval. Use when the user says capture, run capture, or refresh the brief.
allowed-tools: Bash(git *) Bash(gh *) Bash("/c/Program Files/GitHub CLI/gh.exe" *) Bash(python *) Bash(date *) Bash(tail *)
---

Keep this session's own reading small. The subagent does the reading.

`gh` may not be on PATH. If it fails, use `"/c/Program Files/GitHub CLI/gh.exe"`.
On Windows, if bare `python` opens the Microsoft Store stub, use the full path to `python.exe`.

1. Check the tree: `git status --porcelain`. If it is not clean, stop and report.
   `git checkout main && git pull --ff-only` (skip the pull if no remote yet).
2. Create the branch: `git checkout -b capture/<UTC date and time, YYYY-MM-DD-HHMM>`.
3. Pick the mode. **Live** is the default: the subagent reads Drive and GitHub.
   **Staged** is for a run with no Drive access, such as a test round or a
   clone of the public repo. For staged mode, read the cursor
   (`tail -n 1 log.md`) and run `python scripts/stage_sources.py --since <cursor>`.
4. Run the `card-extractor` subagent with this task:
   "Run one capture for Project Alpha in <live or staged> mode. Follow your steps exactly."
   If `python` is not on PATH, add: "Python is at <path>."
5. Save the GitHub items that the new output cites, so the checks run offline:
   `python scripts/snapshot_github.py --cited` (live mode only).
6. Run the checks. The subagent already ran them and fixed what it could. This
   run is the record.
   - `python scripts/redaction_check.py learnings/approved brief.md relations.json`
     If it reports hits in a new card, the brief or the ledger, remove the hit
     text by Edit, then run the check again. Count the hits fixed.
   - `python scripts/provenance_check.py --no-review`
   - `python scripts/relations_check.py`
   Do not fix a provenance or relation failure by hand. Copy each `FAIL` line
   into the PR description, so the reviewer sees it before the merge.
7. Append one line to `log.md`:
   `<new_cursor> | capture | cursor=<new_cursor> | drive=<n> gh=<issues>/<prs>/<files> cards=<n> dropped=<n> relations=<contradictions>/<supersessions>/<scope> regex_fixes=<n> gate=<gate_before>-><gate_after> | <problems or ok>`
8. If no card and no brief change was written, discard the branch
   (`git checkout main && git branch -D <branch>`), but still commit the log line
   on `main`, and report "nothing new".
9. Otherwise commit on the branch: `git add -A && git commit -m "capture: <date>"`.
   Push and open a PR:
   `gh pr create --title "Capture <date>: <n> cards" --body "<the subagent's return block, regex_fixes, and every FAIL line from step 6>"`.
10. Report in three lines: the PR URL, the counts, and anything that failed.
    Do not merge the PR. Merging is the human approval step.
