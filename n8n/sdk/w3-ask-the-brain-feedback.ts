const search = tool({
  type: '@n8n/n8n-nodes-langchain.toolWorkflow', version: 2.2,
  config: { name: 'search_approved_cards', position: [400, 520],
    parameters: {
      description: 'Search the company\'s approved learning cards. Use for any question about project lessons, decisions or risks. Returns up to 3 cards with their id, or says no approved learning covers the question.',
      source: 'database',
      workflowId: { __rl: true, mode: 'id', value: '<WORKFLOW_ID_W3a_logged>' },
      workflowInputs: { mappingMode: 'defineBelow',
        value: { query: fromAi('query', 'The user question in plain words', 'string'), source: 'production' },
        schema: [{ id: 'query', displayName: 'query', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }] } } }
});
const rate = tool({
  type: '@n8n/n8n-nodes-langchain.toolWorkflow', version: 2.2,
  config: { name: 'rate_answer', position: [640, 520],
    parameters: {
      description: 'Record the user\'s rating of an answer from search_approved_cards. Call it only when the user says an answer was helpful, wrong, stale, or missing. A person reviews ratings weekly.',
      source: 'database',
      workflowId: { __rl: true, mode: 'id', value: '<WORKFLOW_ID_W3b>' },
      workflowInputs: { mappingMode: 'defineBelow',
        value: {
          question: fromAi('question', 'The question the user asked', 'string'),
          card_id: fromAi('card_id', 'The id of the card the answer cited, or an empty string if none', 'string'),
          verdict: fromAi('verdict', 'One of: helpful, wrong, stale, missing', 'string'),
          note: fromAi('note', 'A short reason in the user\'s words, under 30 words', 'string'),
          source: 'production' },
        schema: [{ id: 'question', displayName: 'question', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'card_id', displayName: 'card_id', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'verdict', displayName: 'verdict', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'note', displayName: 'note', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true },
                 { id: 'source', displayName: 'source', required: false, defaultMatch: false, display: true, type: 'string', canBeUsedToMatch: true }] } } }
});
const brief = tool({
  type: 'n8n-nodes-base.httpRequestTool', version: 4.5,
  config: { name: 'get_brief', position: [880, 520],
    parameters: {
      toolDescription: 'Get the current one-page project brief: status, key dates, decisions, open risks, open conflicts and supersessions, each fact with its source.',
      url: 'https://api.github.com/repos/eraserhead21/company-brain-poc/contents/brief.md?ref=main',
      authentication: 'predefinedCredentialType', nodeCredentialType: 'githubApi',
      sendHeaders: true, headerParameters: { parameters: [{ name: 'Accept', value: 'application/vnd.github.raw' }] },
      options: {}, optimizeResponse: true, responseType: 'text', truncateResponse: true, maxLength: 6000 },
    credentials: { githubApi: { id: '<GITHUB_CREDENTIAL_ID>', name: 'GitHub account' } } }
});
const server = trigger({
  type: '@n8n/n8n-nodes-langchain.mcpTrigger', version: 2.1,
  config: { name: 'MCP Server Trigger', position: [640, 300],
    parameters: {
      authentication: 'bearerAuth',
      path: 'w3-ask-the-brain-v2',
      instructions: 'Answer only from these tools. Cite the card id for every claim. If no approved card covers the question, say "No approved learning covers this" and stop. Never guess. If the user says an answer was helpful, wrong, stale, or missing, call rate_answer once with the question, the card id and their reason.\n' },
    credentials: { httpBearerAuth: { id: '<BEARER_CREDENTIAL_ID>', name: 'Bearer Auth account' } },
    subnodes: { tools: [search, rate, brief] } },
  output: [{}]
});
export default workflow('w3-feedback', 'W3 Ask the brain (feedback)')
  .add(server);
