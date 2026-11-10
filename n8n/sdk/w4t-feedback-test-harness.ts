const runIt = trigger({
  type: 'n8n-nodes-base.scheduleTrigger', version: 1.4,
  config: { name: 'Test run', position: [240, 300],
    parameters: { rule: { interval: [{ field: 'weeks', weeksInterval: 52, triggerAtDay: [0], triggerAtHour: 3 }] } } },
  output: [{}]
});
const qs = node({
  type: 'n8n-nodes-base.code', version: 2,
  config: { name: 'Five test questions', position: [480, 300], parameters: { jsCode: "return [\n  'When should we start customer sandbox access requests?',\n  'Why store meter readings in UTC?',\n  'Why reconcile against real invoices?',\n  'When was the engineer on sick leave?',\n  'Call me on +31 6 1234 5678 about the firmware contact',\n].map(q => ({ json: { query: q, source: 'test' } }));\n" } },
  output: [{ query: 'q', source: 'test' }]
});
const ask = node({
  type: 'n8n-nodes-base.executeWorkflow', version: 1.4,
  config: { name: 'Ask the logged card search', position: [720, 300],
    parameters: { source: 'database', mode: 'each',
      workflowId: { __rl: true, mode: 'id', value: '<WORKFLOW_ID_W3a_logged>' },
      workflowInputs: { mappingMode: 'defineBelow', value: { query: expr('{{ $json.query }}'), source: expr('{{ $json.source }}') },
        schema: [{ id: 'query', displayName: 'query', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }] },
      options: { waitForSubWorkflow: true } } },
  output: [{ result: 'r', card_ids: '', outcome: 'hit' }]
});
const rate = node({
  type: 'n8n-nodes-base.executeWorkflow', version: 1.4,
  config: { name: 'Rate one answer', position: [960, 300], executeOnce: true,
    parameters: { source: 'database', mode: 'once',
      workflowId: { __rl: true, mode: 'id', value: '<WORKFLOW_ID_W3b>' },
      workflowInputs: { mappingMode: 'defineBelow', value: { question: 'Why store meter readings in UTC?', card_id: expr("{{ $('Ask the logged card search').all()[1].json.card_ids.split(',')[0] }}"), verdict: 'helpful', note: 'Clear and cited.', source: 'test' },
        schema: [{ id: 'question', displayName: 'question', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'card_id', displayName: 'card_id', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'verdict', displayName: 'verdict', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'note', displayName: 'note', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }] },
      options: { waitForSubWorkflow: true } } },
  output: [{ result: 'Rating saved: helpful.' }]
});
export default workflow('w4t-harness', 'W4t Feedback test harness')
  .add(runIt).to(qs).to(ask).to(rate);
