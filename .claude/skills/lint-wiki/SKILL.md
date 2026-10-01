---
name: lint-wiki
description: Health-check the Project Alpha wiki through the Haiku wiki-linter subagent. Finds contradictions, stale claims, orphan cards, duplicates and redaction misses, and writes lint-report.md. Use when the user says lint, lint the wiki, or check the wiki.
allowed-tools: Bash(git *) Bash(date *)
---

1. Make sure you are on `main` with a clean tree: `git status --porcelain`.
2. Run the `wiki-linter` subagent with this task:
   "Lint the Project Alpha wiki. Follow your steps exactly."
3. Append one line to `log.md`:
   `<UTC now> | lint | cursor=<copy the last cursor value unchanged> | contradictions=<n> stale=<n> orphans=<n> duplicates=<n> redaction=<n> | ok`
4. Commit `lint-report.md` and `log.md` on `main`: `git commit -am "lint: <date>"`
   (add `lint-report.md` first if it is new). Push if a remote exists.
5. Report the five counts in one line and point to `lint-report.md`.
