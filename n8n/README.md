# n8n workflows

The company brain runs on n8n Cloud with four workflows. These are exports with credentials, IDs and personal data removed.

| File | Workflow | What it does |
|---|---|---|
| `w1-capture.json` | Company brain: capture | A new Google Doc in the project folder is redacted, turned into a learning card by Claude, and opened as a pull request. A doc marked confidential is held, not captured. |
| `w2-error-alerts.json` | W2 Error alerts | When W1, W3 or W3a fails in production, it emails the workflow, the failed node, the error and a link to the run. |
| `w3-ask-the-brain.json` | W3 Ask the brain | An MCP server with two tools, `search_approved_cards` and `get_brief`. It needs a Bearer token. |
| `w3a-card-search.json` | W3a Card search | The sub-workflow behind `search_approved_cards`. It reads only `learnings/approved` on `main`. |

The rule all four follow: agents read only what a person approved. A card reaches `main` only when a person merges its pull request.

## Import

1. In n8n, create a workflow and use **Import from File** for each JSON.
2. Replace each `<CREDENTIAL_ID>` by picking your own credential in the node: Google Drive, GitHub, Anthropic (Header Auth), Gmail and Bearer Auth.
3. In W1, pick your Drive folder in place of `<DRIVE_FOLDER_ID>`.
4. In W3, point `search_approved_cards` at your imported W3a.
5. In W1, W3 and W3a, set **Settings → Error workflow** to W2. Publish W2 first, or it cannot be selected.
