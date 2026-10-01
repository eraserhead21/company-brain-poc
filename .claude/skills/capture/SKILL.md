---
name: capture
description: Run the Project Alpha capture job. Reads only sources changed since the last run (Drive folder, GitHub issues, PRs, repo docs) through the Haiku card-extractor subagent, writes redacted learning cards and a fresh brief.md on a capture branch, then opens a PR for human approval. Use when the user says capture, run capture, or refresh the brief.
allowed-tools: Bash(git *) Bash(gh *) Bash("/c/Program Files/GitHub CLI/gh.exe" *) Bash("/c/Users/abhis/AppData/Local/Programs/Python/Python313/python.exe" *) Bash(date *)
---

Keep this session's own reading small. The subagent does the reading.

`gh` may not be on PATH. If it fails, use `"/c/Program Files/GitHub CLI/gh.exe"`.

1. Check the tree: `git status --porcelain`. If it is not clean, stop and report.
   `git checkout main && git pull --ff-only` (skip the pull if no remote yet).
2. Create the branch: `git checkout -b capture/<UTC date and time, YYYY-MM-DD-HHMM>`.
3. Run the `card-extractor` subagent with this task:
   "Run one capture for Project Alpha. Follow your steps exactly."
4. Run the redaction check:
   `"/c/Users/abhis/AppData/Local/Programs/Python/Python313/python.exe" scripts/redaction_check.py learnings/approved brief.md`
   Bare `python` hits the Microsoft Store stub on this machine. Use the full path.
   If it reports hits in a new card or the brief, remove the hit text by Edit,
   then run the check again. Count the hits fixed.
5. Append one line to `log.md`:
   `<new_cursor> | capture | cursor=<new_cursor> | drive=<n> gh=<issues>/<prs>/<files> cards=<n> dropped=<n> conflicts=<n> superseded=<n> regex_fixes=<n> | <problems or ok>`
6. If no card and no brief change was written, discard the branch
   (`git checkout main && git branch -D <branch>`), but still commit the log line
   on `main`, and report "nothing new".
7. Otherwise commit on the branch: `git add -A && git commit -m "capture: <date>"`.
   Push and open a PR:
   `gh pr create --title "Capture <date>: <n> cards" --body "<the subagent's return block, plus regex_fixes>"`.
8. Report in three lines: the PR URL, the counts, and anything that failed.
   Do not merge the PR. Merging is the human approval step.
