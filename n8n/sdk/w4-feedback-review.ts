const weekly = trigger({
  type: 'n8n-nodes-base.scheduleTrigger', version: 1.4,
  config: { name: 'Weekly, Monday 09:00', position: [240, 300],
    parameters: { rule: { interval: [{ field: 'weeks', weeksInterval: 1, triggerAtDay: [1], triggerAtHour: 9, triggerAtMinute: 0 }] } } },
  output: [{}]
});
const getLog = node({
  type: 'n8n-nodes-base.dataTable', version: 1.1,
  config: { name: 'Get question log', position: [480, 300], alwaysOutputData: true,
    parameters: { resource: 'row', operation: 'get', dataTableId: { __rl: true, mode: 'id', value: '<TABLE_ID_cb_question_log>' }, returnAll: true } },
  output: [{ question: 'q', outcome: 'coverage_gap', source: 'production', redactions: 0 }]
});
const getRatings = node({
  type: 'n8n-nodes-base.dataTable', version: 1.1,
  config: { name: 'Get answer ratings', position: [720, 300], alwaysOutputData: true, executeOnce: true,
    parameters: { resource: 'row', operation: 'get', dataTableId: { __rl: true, mode: 'id', value: '<TABLE_ID_cb_answer_ratings>' }, returnAll: true } },
  output: [{ question: 'q', verdict: 'helpful', card_id: 'id', source: 'production' }]
});
const getCases = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.5,
  config: { name: 'Get current cases', position: [960, 300], executeOnce: true, alwaysOutputData: true, onError: 'continueRegularOutput',
    parameters: { url: 'https://api.github.com/repos/eraserhead21/company-brain-poc/contents/tests/answers/feedback_cases.json?ref=main', authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi', sendHeaders: true, headerParameters: { parameters: [{ name: 'Accept', value: 'application/vnd.github+json' }] }, options: {} },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } },
  output: [{ content: 'e30=', sha: 'abc' }]
});
const build = node({
  type: 'n8n-nodes-base.code', version: 2,
  config: { name: 'Propose eval cases', position: [1200, 300], parameters: { jsCode: "// Turn production signals into proposed eval cases. A person approves them by merging the PR.\nconst logRows = $('Get question log').all().map(i => i.json).filter(r => r.question && r.source !== 'regression');\nconst rateRows = $('Get answer ratings').all().map(i => i.json).filter(r => r.verdict && r.source !== 'regression');\nconst cur = $('Get current cases').first().json;\nlet existing = { version: 1, cases: [] };\nif (cur && cur.content) {\n  existing = JSON.parse(Buffer.from(cur.content, 'base64').toString('utf8'));\n}\nconst known = new Set(existing.cases.map(c => c.question.toLowerCase()));\nconst today = new Date().toISOString().slice(0, 10);\nconst proposed = [];\nlet n = existing.cases.length;\nfunction add(c) {\n  const key = c.question.toLowerCase();\n  if (known.has(key)) return;\n  known.add(key);\n  n += 1;\n  proposed.push(Object.assign({ id: 'fb-' + String(n).padStart(3, '0'), status: 'proposed', first_seen: today }, c));\n}\n\n// Coverage gaps, most-missed first.\nconst gaps = {};\nfor (const r of logRows.filter(r => r.outcome === 'coverage_gap')) {\n  const g = gaps[r.question] || { count: 0, redacted: r.redactions > 0 };\n  g.count += 1;\n  gaps[r.question] = g;\n}\nconst gapList = Object.entries(gaps).sort((a, b) => b[1].count - a[1].count);\nfor (const [question, g] of gapList) {\n  add(g.redacted\n    ? { question, expected: 'coverage_gap', needs_decision: false,\n        signal: 'question_log: ' + g.count + ' coverage gap(s), question held personal or commercial data',\n        reviewer_note: 'Guardrail case: this question must stay refused.' }\n    : { question, expected: 'coverage_gap', needs_decision: true,\n        signal: 'question_log: ' + g.count + ' coverage gap(s)',\n        reviewer_note: 'Write a card and set expected to its id, or keep coverage_gap if it is out of scope.' });\n}\n\n// User ratings.\nfor (const r of rateRows) {\n  if (!r.question) continue;\n  if (r.verdict === 'helpful' && r.card_id) {\n    add({ question: r.question, expected: r.card_id, needs_decision: false, signal: 'rating: helpful' });\n  } else {\n    add({ question: r.question, expected: r.card_id || 'coverage_gap', needs_decision: true,\n          signal: 'rating: ' + r.verdict + (r.card_id ? ' on ' + r.card_id : ''),\n          reviewer_note: r.note || 'Review the card, then set expected.' });\n  }\n}\n\nif (!proposed.length) return [];\nconst next = { version: 1, cases: existing.cases.concat(proposed) };\nconst stamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 13);\nconst top = gapList.slice(0, 5).map(([q, g]) => '- ' + g.count + 'x: ' + q).join('\\n') || '- none';\nconst poor = rateRows.filter(r => r.verdict !== 'helpful').map(r => '- ' + r.verdict + ': ' + (r.card_id || 'no card') + ' (' + r.question + ')').join('\\n') || '- none';\nconst body = [\n  'Weekly feedback review from W4. Merge = approve these eval cases. Close = reject.',\n  '',\n  'Questions logged: ' + logRows.length + '. Coverage gaps: ' + logRows.filter(r => r.outcome === 'coverage_gap').length + '. Ratings: ' + rateRows.length + '.',\n  '',\n  'Most-missed questions:',\n  top,\n  '',\n  'Cards rated wrong, stale or missing:',\n  poor,\n  '',\n  'Proposed cases: ' + proposed.length + '. Cases with needs_decision: true need a person to set expected before W4b runs them.',\n].join('\\n');\nreturn [{ json: {\n  branch: 'feedback/n8n-' + stamp,\n  path: 'tests/answers/feedback_cases.json',\n  sha: cur && cur.sha ? cur.sha : null,\n  contentB64: Buffer.from(JSON.stringify(next, null, 2) + '\\n', 'utf8').toString('base64'),\n  count: proposed.length,\n  title: 'Feedback review (n8n): ' + proposed.length + ' proposed eval case(s)',\n  body,\n} }];\n" } },
  output: [{ branch: 'feedback/n8n-x', path: 'tests/answers/feedback_cases.json', sha: null, contentB64: 'e30=', count: 2, title: 't', body: 'b' }]
});
const mainRef = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.5,
  config: { name: 'Get main commit', position: [1440, 300],
    parameters: { url: 'https://api.github.com/repos/eraserhead21/company-brain-poc/git/ref/heads/main', authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi', sendHeaders: true, headerParameters: { parameters: [{ name: 'Accept', value: 'application/vnd.github+json' }] }, options: {} },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } },
  output: [{ object: { sha: 'abc' } }]
});
const branch = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.5,
  config: { name: 'Create feedback branch', position: [1680, 300],
    parameters: { method: 'POST', url: 'https://api.github.com/repos/eraserhead21/company-brain-poc/git/refs', authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi', sendHeaders: true, headerParameters: { parameters: [{ name: 'Accept', value: 'application/vnd.github+json' }] },
      sendBody: true, specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify({ ref: 'refs/heads/' + $('Propose eval cases').first().json.branch, sha: $json.object.sha }) }}"), options: {} },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } },
  output: [{ ref: 'refs/heads/feedback/n8n-x' }]
});
const putFile = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.5,
  config: { name: 'Write proposed cases', position: [1920, 300],
    parameters: { method: 'PUT', url: expr("https://api.github.com/repos/eraserhead21/company-brain-poc/contents/{{ $('Propose eval cases').first().json.path }}"), authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi', sendHeaders: true, headerParameters: { parameters: [{ name: 'Accept', value: 'application/vnd.github+json' }] },
      sendBody: true, specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify(Object.assign({ message: 'feedback (n8n): ' + $('Propose eval cases').first().json.count + ' proposed eval case(s)', content: $('Propose eval cases').first().json.contentB64, branch: $('Propose eval cases').first().json.branch }, $('Propose eval cases').first().json.sha ? { sha: $('Propose eval cases').first().json.sha } : {})) }}"), options: {} },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } },
  output: [{ content: { path: 'tests/answers/feedback_cases.json' } }]
});
const openPr = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.5,
  config: { name: 'Open feedback pull request', position: [2160, 300],
    parameters: { method: 'POST', url: 'https://api.github.com/repos/eraserhead21/company-brain-poc/pulls', authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi', sendHeaders: true, headerParameters: { parameters: [{ name: 'Accept', value: 'application/vnd.github+json' }] },
      sendBody: true, specifyBody: 'json',
      jsonBody: expr("{{ JSON.stringify({ title: $('Propose eval cases').first().json.title, head: $('Propose eval cases').first().json.branch, base: 'main', body: $('Propose eval cases').first().json.body }) }}"), options: {} },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } },
  output: [{ html_url: 'https://github.com/x/pull/1' }]
});
export default workflow('w4-feedback', 'W4 Feedback review')
  .add(weekly).to(getLog).to(getRatings).to(getCases).to(build).to(mainRef).to(branch).to(putFile).to(openPr)
  .group('Read the signals', [getLog, getRatings, getCases], { description: 'Reads the question log, the answer ratings, and the eval cases already approved on main.' })
  .group('Propose cases', [build], { description: 'Turns coverage gaps and poor ratings into proposed eval cases. Stops when nothing is new.' })
  .group('Open the review PR', [mainRef, branch, putFile, openPr], { description: 'Opens a PR on a feedback/ branch. A person approves the cases by merging it. Never writes to main.' });
