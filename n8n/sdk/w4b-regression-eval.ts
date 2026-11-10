const weekly = trigger({
  type: 'n8n-nodes-base.scheduleTrigger', version: 1.4,
  config: { name: 'Weekly, Monday 10:00', position: [240, 300],
    parameters: { rule: { interval: [{ field: 'weeks', weeksInterval: 1, triggerAtDay: [1], triggerAtHour: 10, triggerAtMinute: 0 }] } } },
  output: [{}]
});
const prev = node({
  type: 'n8n-nodes-base.dataTable', version: 1.1,
  config: { name: 'Get previous runs', position: [480, 300], alwaysOutputData: true,
    parameters: { resource: 'row', operation: 'get', dataTableId: { __rl: true, mode: 'id', value: '<TABLE_ID_cb_regression_runs>' }, returnAll: false, limit: 1 } },
  output: [{ run_id: 'reg-1' }]
});
const getCases = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.5,
  config: { name: 'Get approved cases', position: [720, 300], executeOnce: true, alwaysOutputData: true, onError: 'continueRegularOutput',
    parameters: { url: 'https://api.github.com/repos/eraserhead21/company-brain-poc/contents/tests/answers/feedback_cases.json?ref=main', authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi', sendHeaders: true, headerParameters: { parameters: [{ name: 'Accept', value: 'application/vnd.github+json' }] }, options: {} },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } },
  output: [{ content: 'e30=' }]
});
const listCases = node({
  type: 'n8n-nodes-base.code', version: 2,
  config: { name: 'List runnable cases', position: [960, 300], parameters: { jsCode: "// List the approved cases that W4b can run: merged to main, with no open decision.\nconst cur = $('Get approved cases').first().json;\nif (!cur || !cur.content) return [];\nconst data = JSON.parse(Buffer.from(cur.content, 'base64').toString('utf8'));\nconst prev = $('Get previous runs').all().map(i => i.json).filter(r => r.run_id);\nconst runId = 'reg-' + new Date().toISOString().replace(/[-:]/g, '').slice(0, 13);\nreturn data.cases\n  .filter(c => !c.needs_decision)\n  .map(c => ({ json: { run_id: runId, is_baseline: prev.length === 0, case_id: c.id, question: c.question, expected: c.expected } }));\n" } },
  output: [{ run_id: 'reg-1', is_baseline: true, case_id: 'fb-001', question: 'q', expected: 'coverage_gap' }]
});
const ask = node({
  type: 'n8n-nodes-base.executeWorkflow', version: 1.4,
  config: { name: 'Ask the logged card search', position: [1200, 300],
    parameters: { source: 'database', mode: 'each',
      workflowId: { __rl: true, mode: 'id', value: '<WORKFLOW_ID_W3a_logged>' },
      workflowInputs: { mappingMode: 'defineBelow', value: { query: expr('{{ $json.question }}'), source: 'regression' },
        schema: [{ id: 'query', displayName: 'query', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }] },
      options: { waitForSubWorkflow: true } } },
  output: [{ result: 'r', card_ids: '', outcome: 'coverage_gap' }]
});
const score = node({
  type: 'n8n-nodes-base.code', version: 2,
  config: { name: 'Score each case', position: [1440, 300], parameters: { jsCode: "// Pass when the outcome matches: coverage_gap stays refused, or the expected card is in the top 3.\nconst cases = $('List runnable cases').all();\nreturn $input.all().map((it, idx) => {\n  const c = cases[idx].json;\n  const got = it.json.outcome === 'coverage_gap' ? 'coverage_gap' : (it.json.card_ids || '');\n  const passed = c.expected === 'coverage_gap'\n    ? got === 'coverage_gap'\n    : got.split(',').includes(c.expected);\n  return { json: {\n    run_id: c.run_id, run_at: new Date().toISOString(), ref: 'main', case_id: c.case_id,\n    question: c.question, expected: c.expected, got, passed, is_baseline: c.is_baseline,\n  } };\n});\n" } },
  output: [{ run_id: 'reg-1', run_at: '2026-11-10T10:00:00Z', ref: 'main', case_id: 'fb-001', question: 'q', expected: 'coverage_gap', got: 'coverage_gap', passed: true, is_baseline: true }]
});
const save = node({
  type: 'n8n-nodes-base.dataTable', version: 1.1,
  config: { name: 'Write regression results', position: [1680, 300],
    parameters: { resource: 'row', operation: 'insert',
      dataTableId: { __rl: true, mode: 'id', value: '<TABLE_ID_cb_regression_runs>' },
      columns: { mappingMode: 'defineBelow', value: { run_id: expr('{{ $json.run_id }}'), run_at: expr('{{ $json.run_at }}'), ref: expr('{{ $json.ref }}'), case_id: expr('{{ $json.case_id }}'), question: expr('{{ $json.question }}'), expected: expr('{{ $json.expected }}'), got: expr('{{ $json.got }}'), passed: expr('{{ $json.passed }}'), is_baseline: expr('{{ $json.is_baseline }}') }, schema: [{ id: 'run_id', displayName: 'run_id', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'run_at', displayName: 'run_at', required: false, defaultMatch: false, display: true, type: 'dateTime', canBeUsedToMatch: true }, { id: 'ref', displayName: 'ref', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'case_id', displayName: 'case_id', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'question', displayName: 'question', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'expected', displayName: 'expected', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'got', displayName: 'got', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'passed', displayName: 'passed', required: false, defaultMatch: false, display: true, type: 'boolean', canBeUsedToMatch: true }, { id: 'is_baseline', displayName: 'is_baseline', required: false, defaultMatch: false, display: true, type: 'boolean', canBeUsedToMatch: true }] } } },
  output: [{ id: 1 }]
});
export default workflow('w4b-regression', 'W4b Regression eval')
  .add(weekly).to(prev).to(getCases).to(listCases).to(ask).to(score).to(save)
  .group('Load the regression eval set', [prev, getCases, listCases], { description: 'Reads the approved cases on main. Skips cases that still need a decision. The first run is the baseline.' })
  .group('Run and score', [ask, score, save], { description: 'Asks each question through the logged search, scores pass or fail, and writes one row per case.' });
