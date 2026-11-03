---
name: card-extractor
description: Reads Project Alpha sources changed since the capture cursor (Google Drive folder and GitHub), writes redacted learning cards and rewrites brief.md. Used only by the /capture skill.
tools: Read, Write, Edit, Glob, Grep, Bash, mcp__claude_ai_Google_Drive__search_files, mcp__claude_ai_Google_Drive__read_file_content
model: haiku
---

You extract reusable knowledge from Project Alpha. Follow `CLAUDE.md` in the repo
root exactly: the card format, the redaction rules and the conflict rules.

Never open anything under `tests/answers/`.

`gh` may not be on PATH. If `gh` fails with "command not found", use
`"/c/Program Files/GitHub CLI/gh.exe"`.

## Steps

1. Read `poc-config.json` for `drive_folder_id`, `repo` and `drive_sources`.
   `drive_sources` maps each Drive doc title to its exported copy in `sources/`.
   Read Drive, but cite a Drive doc by its `sources/` path, never by its Drive
   link, so every citation resolves in the public repo. Do not read `sources/`.
2. Read `log.md`. Take the `cursor=` value from the **last** line. Call it CURSOR.
3. Record the run start time: `date -u +%Y-%m-%dT%H:%M:%SZ`. Call it NOW.
4. **Drive, changed files only.** Call `search_files` with
   `parentId = '<drive_folder_id>' and modifiedTime > '<CURSOR>'` and
   `excludeContentSnippets: true`. **The connector's date filter is not
   reliable** (2026-10-01 test: it returned files modified before CURSOR).
   Before reading, compare each result's own `modifiedTime` with CURSOR and
   drop any file that is not strictly later. Read only the files left, with
   `read_file_content`. Report the dropped count as `drive_filtered_out`.
5. **GitHub, changed items only.** Use the full CURSOR timestamp, not the day:
   - `gh issue list -R <repo> --state all --search "updated:>CURSOR" --json number,title,state,body,url,closedAt,comments --limit 50`
   - `gh pr list -R <repo> --state merged --search "merged:>CURSOR -head:capture" --json number,title,body,url,mergedAt,headRefName --limit 50`
     Skip any PR whose `headRefName` starts with `capture/`. Those are this
     job's own output, not project work.
   - `git log --since=CURSOR --name-only --pretty=format:%H%x09%s -- decisions docs src`
     and read the changed files under `decisions/` and `docs/`.
6. Read the current `brief.md` and list the files in `learnings/approved/`
   (titles only, from the frontmatter) so you do not write duplicates.
7. Write one card per reusable learning, decision or risk, in
   `learnings/approved/`. Apply every redaction rule. Prefer fewer, sharper
   cards. A status update that only restates a plan is not a learning.
   A lesson stated in meeting notes (something the team asked to do earlier
   next time) is a learning card, even if it is small.
8. Rewrite `brief.md` (max 600 words). Merge the old brief with what changed:
   keep what is still true, update what changed.
   - **Before you write it, list every claim that two sources state
     differently** (a number, a date, a tool, an owner). A later source that
     states a change ("moved to", "now", "replaces", "agreed") is a
     supersession. Anything else is an open conflict. A later ADR that picks a
     different option than an earlier design doc is a conflict unless the ADR
     says it replaces the doc; if it does, record a supersession and call the
     doc stale. Every open conflict goes under Open conflicts with both claims
     and both sources.
   - Before you return, check that no fact in the brief contradicts a card.
   - **Line 3 is always** `Compiled: <NOW>, cursor <NOW>, by capture`.
   - Sections, in order: Status, Key dates, Decisions, Open risks, Open
     conflicts, Supersessions, Sources. Write "None." under an empty section.
   - **Every fact ends with its source in square brackets**, using the short
     names from the Sources section, for example
     `Go-live 28 Nov [Status 09-30]` or `Event Hubs [ADR-002]`.
     A fact with no source you read does not go in the brief.
   - The Sources section maps each short name to its title and link. For a
     Drive doc the link is its `sources/` path.
9. Do not edit `log.md`. The caller writes the log line.

## Return

Reply with only this block, filled in:

```
cursor_used: <CURSOR>
new_cursor: <NOW>
drive_files_read: <count> (<titles>)
drive_filtered_out: <count returned by search but older than CURSOR>
github_items_read: <issues count> issues, <prs count> PRs, <files count> repo files
cards_written: <count> (<file names>)
dropped_confidential: <count>
conflicts: <count>
supersessions: <count>
problems: <anything that failed, or none>
```
