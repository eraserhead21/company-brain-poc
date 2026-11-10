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

## Live fixes

The first live run of W1 failed four times. Each fix is in the exports above.

1. **"This credential is configured to prevent use within an HTTP Request node."** n8n Cloud does not let its managed Google sign-in run inside an HTTP Request node. Fix: a Google Drive "Download file" node (Google Docs converted to text), then "Extract from File".
2. **"Authorization failed."** The Header Auth credential did not send the key as the `x-api-key` header. Fix: set the header name and value correctly.
3. **"Method not allowed."** The Claude request node had changed to PUT. Fix: back to POST.
4. **Every document fell through as "no card".** Claude's reply can start with a block that is not text, and the code read the first block. Fix: read the block whose `type` is `text`.
