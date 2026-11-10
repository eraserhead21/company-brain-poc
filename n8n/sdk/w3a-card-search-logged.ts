const callIn = trigger({
  type: 'n8n-nodes-base.executeWorkflowTrigger', version: 1.3,
  config: { name: 'When called by W3 or W4b', position: [240, 300],
    parameters: { inputSource: 'workflowInputs', workflowInputs: { values: [{ name: 'query', type: 'string' }, { name: 'source', type: 'string' }] } } },
  output: [{ query: 'Why store meter readings in UTC?', source: 'production' }]
});
const listCards = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.5,
  config: { name: 'List cards', position: [480, 300],
    parameters: { url: 'https://api.github.com/repos/eraserhead21/company-brain-poc/contents/learnings/approved?ref=main', authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi', options: {} },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } },
  output: [{ name: 'card.md', url: 'https://api.github.com/repos/eraserhead21/company-brain-poc/contents/learnings/approved/card.md?ref=main' }]
});
const getCard = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.5,
  config: { name: 'Get card', position: [720, 300],
    parameters: { url: expr('{{ $json.url }}'), authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi',
      sendHeaders: true, headerParameters: { parameters: [{ name: 'Accept', value: 'application/vnd.github.raw' }] },
      options: { response: { response: { responseFormat: 'text' } } } },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } },
  output: [{ data: 'id: card' }]
});
const rank = node({
  type: 'n8n-nodes-base.code', version: 2,
  config: { name: 'Rank cards', position: [960, 300], parameters: { jsCode: "// W3a ranking, unchanged, plus the card IDs and a hit or coverage_gap outcome.\nconst q = $('When called by W3 or W4b').first().json.query || '';\nconst stop = new Set(['what','when','which','where','does','about','should','would','could','there','their','this','that','with','from','have','engineer','project','learn','learned','lesson','lessons']);\nconst words = q.toLowerCase().split(/\\W+/).filter(w => w.length > 3 && !stop.has(w));\nconst scored = $input.all()\n  .map(i => i.json.data || '')\n  .map(t => ({ t, s: words.filter(w => t.toLowerCase().includes(w)).length }))\n  .filter(x => x.s >= Math.min(2, words.length))\n  .sort((a, b) => b.s - a.s)\n  .slice(0, 3);\nif (!words.length || !scored.length) {\n  return [{ json: { result: 'No approved learning covers this.', card_ids: '', outcome: 'coverage_gap' } }];\n}\nconst ids = scored.map(x => ((x.t.match(/^id:\\s*(.+)$/m) || [])[1] || '').trim()).filter(Boolean);\nreturn [{ json: { result: scored.map(x => x.t).join('\\n\\n---\\n\\n'), card_ids: ids.join(','), outcome: 'hit' } }];\n" } },
  output: [{ result: 'No approved learning covers this.', card_ids: '', outcome: 'coverage_gap' }]
});
const shape = node({
  type: 'n8n-nodes-base.code', version: 2,
  config: { name: 'Redact question for the log', position: [1200, 300], parameters: { jsCode: "// Same patterns as W1 and scripts/redaction_check.py. Matches become [redacted:<type>].\nconst P = {\n  email: /[\\w.+-]+@[\\w-]+\\.[\\w.-]+/g,\n  phone: /(?<!\\w)\\+?\\d[\\d \\-]{8,}\\d(?!\\w)/g,\n  money: /[\u00a3$\u20ac]\\s?\\d[\\d.,]*\\s?[kKmM]?/g,\n  secret_word: /\\b(pass(word)?|pwd|api[_ -]?key|token|secret|vpn|wi-?fi|sftp)\\b\\s*[:=]\\s*\\S*/gi,\n  dob: /\\b(dob|date of birth|born)\\b/gi,\n  account_id: /\\b[A-Z]{2,}-ACCT-\\d+\\b/g,\n  hr_words: /\\b(salary|raise|pip|performance improvement|sick|surgery|medical)\\b/gi,\n  commercial: /\\b(margin|penalt(y|ies)|contract value|dispute|switch(ing)? vendor)\\b/gi,\n};\nfunction redact(s) {\n  let n = 0;\n  let t = String(s || '');\n  for (const [k, re] of Object.entries(P)) {\n    t = t.replace(re, m => {\n      if (k === 'phone' && /^\\d{4}-\\d{2}-\\d{2}$/.test(m.trim())) return m;\n      n += 1;\n      return '[redacted:' + k + ']';\n    });\n  }\n  return { text: t.slice(0, 500), n };\n}\n\nconst inp = $('When called by W3 or W4b').first().json;\nconst rank = $input.first().json;\nconst r = redact(inp.query);\nreturn [{ json: {\n  asked_at: new Date().toISOString(),\n  source: inp.source || 'production',\n  tool: 'search_approved_cards',\n  question: r.text,\n  card_ids: rank.card_ids,\n  outcome: rank.outcome,\n  redactions: r.n,\n} }];\n" } },
  output: [{ asked_at: '2026-11-10T10:00:00Z', source: 'production', tool: 'search_approved_cards', question: 'q', card_ids: '', outcome: 'hit', redactions: 0 }]
});
const logIt = node({
  type: 'n8n-nodes-base.dataTable', version: 1.1,
  config: { name: 'Write question log row', position: [1440, 300],
    parameters: { resource: 'row', operation: 'insert',
      dataTableId: { __rl: true, mode: 'id', value: '<TABLE_ID_cb_question_log>' },
      columns: { mappingMode: 'defineBelow', value: { asked_at: expr('{{ $json.asked_at }}'), source: expr('{{ $json.source }}'), tool: expr('{{ $json.tool }}'), question: expr('{{ $json.question }}'), card_ids: expr('{{ $json.card_ids }}'), outcome: expr('{{ $json.outcome }}'), redactions: expr('{{ $json.redactions }}') }, schema: [{ id: 'asked_at', displayName: 'asked_at', required: false, defaultMatch: false, display: true, type: 'dateTime', canBeUsedToMatch: true }, { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'tool', displayName: 'tool', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'question', displayName: 'question', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'card_ids', displayName: 'card_ids', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'outcome', displayName: 'outcome', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }, { id: 'redactions', displayName: 'redactions', required: false, defaultMatch: false, display: true, type: 'number', canBeUsedToMatch: true }] } } },
  output: [{ id: 1 }]
});
const answer = node({
  type: 'n8n-nodes-base.set', version: 3.4,
  config: { name: 'Return the answer', position: [1680, 300],
    parameters: { mode: 'manual', includeOtherFields: false, assignments: { assignments: [
      { id: 'r1', name: 'result', value: expr("{{ $('Rank cards').first().json.result }}"), type: 'string' },
      { id: 'r2', name: 'card_ids', value: expr("{{ $('Rank cards').first().json.card_ids }}"), type: 'string' },
      { id: 'r3', name: 'outcome', value: expr("{{ $('Rank cards').first().json.outcome }}"), type: 'string' }
    ] } } },
  output: [{ result: 'No approved learning covers this.', card_ids: '', outcome: 'coverage_gap' }]
});
export default workflow('w3a-logged', 'W3a Card search (logged)')
  .add(callIn).to(listCards).to(getCard).to(rank).to(shape).to(logIt).to(answer)
  .group('Search approved cards', [listCards, getCard, rank], { description: 'Same keyword search as W3a: reads only learnings/approved on main and returns up to 3 cards.' })
  .group('Production log', [shape, logIt, answer], { description: 'Redacts the question with the W1 patterns, writes one row to cb_question_log, then returns the answer.' });
