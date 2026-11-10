# n8n workflows

The company brain runs on n8n Cloud with four workflows. These are exports with credentials, IDs and personal data removed.

| File | Workflow | What it does |
|---|---|---|
| `w1-capture.json` | Company brain: capture | A new Google Doc in the project folder is redacted, turned into a learning card by Claude, and opened as a pull request. A doc marked confidential is held, not captured. |
| `w2-error-alerts.json` | W2 Error alerts | When W1, W3 or W3a fails in production, it emails the workflow, the failed node, the error and a link to the run. |
| `w3-ask-the-brain.json` | W3 Ask the brain | An MCP server with two tools, `search_approved_cards` and `get_brief`. It needs a Bearer token. |
| `w3a-card-search.json` | W3a Card search | The sub-workflow behind `search_approved_cards`. It reads only `learnings/approved` on `main`. |

The rule all four follow: agents read only what a person approved. A card reaches `main` only when a person merges its pull request.

## Feedback loop workflows

These workflows add the outer feedback loop. Their sources are in [`sdk/`](sdk/) as n8n Workflow SDK code, with credential, table, and workflow IDs replaced by placeholders. Recreate them with the n8n MCP server's `create_workflow_from_code` tool, then pick your own credentials.

| File | Workflow | What it does |
|---|---|---|
| `sdk/w3a-card-search-logged.ts` | W3a Card search (logged) | The W3a search, plus one redacted row per question in the `cb_question_log` Data Table. |
| `sdk/w3b-rate-answer.ts` | W3b Rate answer | The sub-workflow behind the `rate_answer` tool. Writes one redacted row to `cb_answer_ratings`. |
| `sdk/w3-ask-the-brain-feedback.ts` | W3 Ask the brain (feedback) | W3 with three tools: `search_approved_cards` (logged), `rate_answer`, and `get_brief`. |
| `sdk/w4-feedback-review.ts` | W4 Feedback review | Every Monday, proposes eval cases from coverage gaps and ratings in a PR on a `feedback/` branch. |
| `sdk/w4b-regression-eval.ts` | W4b Regression eval | Reruns the approved cases on `main` and writes pass or fail to `cb_regression_runs`. |
| `sdk/w4t-feedback-test-harness.ts` | W4t Feedback test harness | Sends 5 fictional test questions and 1 rating through the loop. |

Create the three Data Tables first: `cb_question_log`, `cb_answer_ratings`, and `cb_regression_runs`. The column names are in the insert nodes.

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
