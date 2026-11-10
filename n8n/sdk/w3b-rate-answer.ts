const callIn = trigger({
  type: 'n8n-nodes-base.executeWorkflowTrigger', version: 1.3,
  config: { name: 'When called by W3', position: [240, 300],
    parameters: { inputSource: 'workflowInputs', workflowInputs: { values: [
      { name: 'question', type: 'string' }, { name: 'card_id', type: 'string' }, { name: 'verdict', type: 'string' },
      { name: 'note', type: 'string' }, { name: 'source', type: 'string' } ] } } },
  output: [{ question: 'q', card_id: '', verdict: 'helpful', note: '', source: 'production' }]
});
const shape = node({
  type: 'n8n-nodes-base.code', version: 2,
  config: { name: 'Check and redact the rating', position: [480, 300], parameters: { jsCode: "// Same patterns as W1 and scripts/redaction_check.py. Matches become [redacted:<type>].\nconst P = {\n  email: /[\\w.+-]+@[\\w-]+\\.[\\w.-]+/g,\n  phone: /(?<!\\w)\\+?\\d[\\d \\-]{8,}\\d(?!\\w)/g,\n  money: /[\u00a3$\u20ac]\\s?\\d[\\d.,]*\\s?[kKmM]?/g,\n  secret_word: /\\b(pass(word)?|pwd|api[_ -]?key|token|secret|vpn|wi-?fi|sftp)\\b\\s*[:=]\\s*\\S*/gi,\n  dob: /\\b(dob|date of birth|born)\\b/gi,\n  account_id: /\\b[A-Z]{2,}-ACCT-\\d+\\b/g,\n  hr_words: /\\b(salary|raise|pip|performance improvement|sick|surgery|medical)\\b/gi,\n  commercial: /\\b(margin|penalt(y|ies)|contract value|dispute|switch(ing)? vendor)\\b/gi,\n};\nfunction redact(s) {\n  let n = 0;\n  let t = String(s || '');\n  for (const [k, re] of Object.entries(P)) {\n    t = t.replace(re, m => {\n      if (k === 'phone' && /^\\d{4}-\\d{2}-\\d{2}$/.test(m.trim())) return m;\n      n += 1;\n      return '[redacted:' + k + ']';\n    });\n  }\n  return { text: t.slice(0, 500), n };\n}\n\nconst inp = $input.first().json;\nconst allowed = ['helpful', 'wrong', 'stale', 'missing'];\nconst verdict = String(inp.verdict || '').toLowerCase().trim();\nif (!allowed.includes(verdict)) {\n  throw new Error('verdict must be one of: ' + allowed.join(', '));\n}\nconst q = redact(inp.question);\nconst note = redact(inp.note);\nreturn [{ json: {\n  rated_at: new Date().toISOString(),\n  source: inp.source || 'production',\n  question: q.text,\n  card_id: String(inp.card_id || '').trim(),\n  verdict,\n  note: note.text,\n  redactions: q.n + note.n,\n} }];\n" } },
  output: [{ rated_at: '2026-11-10T10:00:00Z', source: 'production', question: 'q', card_id: '', verdict: 'helpful', note: '', redactions: 0 }]
});
const save = node({
  type: 'n8n-nodes-base.dataTable', version: 1.1,
  config: { name: 'Write rating row', position: [720, 300],
    parameters: { resource: 'row', operation: 'insert',
      dataTableId: { __rl: true, mode: 'id', value: '<TABLE_ID_cb_answer_ratings>' },
      columns: { mappingMode: 'defineBelow', value: { rated_at: expr('{{ $json.rated_at }}'), source: expr('{{ $json.source }}'), question: expr('{{ $json.question }}'), card_id: expr('{{ $json.card_id }}'), verdict: expr('{{ $json.verdict }}'), note: expr('{{ $json.note }}'), redactions: expr('{{ $json.redactions }}') }, schema: [{ id: 'rated_at', displayName: 'rated_at', required: false, defaultMatch: false, display: true, type: 'dateTime', canBeUsedToMatch: true }, { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'question', displayName: 'question', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'card_id', displayName: 'card_id', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'verdict', displayName: 'verdict', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'note', displayName: 'note', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'redactions', displayName: 'redactions', required: false, defaultMatch: false, display: true, type: 'number', canBeUsedToMatch: true }] } } },
  output: [{ id: 1 }]
});
const reply = node({
  type: 'n8n-nodes-base.set', version: 3.4,
  config: { name: 'Confirm the rating', position: [960, 300],
    parameters: { mode: 'manual', includeOtherFields: false, assignments: { assignments: [
      { id: 'c1', name: 'result', value: expr("Rating saved: {{ $('Check and redact the rating').first().json.verdict }}. A person reviews ratings weekly."), type: 'string' }
    ] } } },
  output: [{ result: 'Rating saved: helpful.' }]
});
export default workflow('w3b-rate', 'W3b Rate answer')
  .add(callIn).to(shape).to(save).to(reply)
  .group('User rating', [shape, save, reply], { description: 'Checks the verdict, redacts the question and note, and writes one row to cb_answer_ratings.' });
