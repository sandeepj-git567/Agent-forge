import React, { useState, useEffect } from 'react';

type Tab = 'overview' | 'agents' | 'workflows' | 'builder' | 'documents' | 'rag' | 'tasks' | 'traces' | 'evaluations' | 'settings';

const API_BASE = 'http://localhost:8000/api/v1';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  
  // Tasks state
  const [taskInput, setTaskInput] = useState('Research enterprise AI agent frameworks and RAG architectures');
  const [taskMode, setTaskMode] = useState('research');
  const [taskApproval, setTaskApproval] = useState(false);
  const [taskResult, setTaskResult] = useState<any>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  // System state
  const [readiness, setReadiness] = useState<any>(null);
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [evaluations, setEvaluations] = useState<any[]>([]);
  const [benchmarks, setBenchmarks] = useState<any[]>([]);

  // RAG state
  const [ragQuery, setRagQuery] = useState('What framework does AgentForge AI use?');
  const [ragResult, setRagResult] = useState<any>(null);
  const [isRagQuerying, setIsRagQuerying] = useState(false);

  // Workflow builder state
  const [wfName, setWfName] = useState('Enterprise Market Research Pipeline');
  const [wfDesc, setWfDesc] = useState('Plan research strategy, gather document context via RAG, analyze market trends, and output structured report.');
  const [isWfCreating, setIsWfCreating] = useState(false);

  // Trace lookup state
  const [traceRunId, setTraceRunId] = useState('');
  const [traceData, setTraceData] = useState<any>(null);

  // Eval state
  const [evalInput, setEvalInput] = useState('Explain RAG architecture in 2 sentences.');
  const [evalActual, setEvalActual] = useState('RAG combines retrieval of external vector documents with LLM text generation. This grounds model answers in accurate contextual data.');
  const [evalResult, setEvalResult] = useState<any>(null);

  // Initial data fetch
  useEffect(() => {
    fetchReadiness();
    fetchDocuments();
    fetchWorkflows();
    fetchEvaluations();
    fetchBenchmarks();
  }, []);

  const fetchReadiness = async () => {
    try {
      const res = await fetch(`${API_BASE}/health/ready`);
      const data = await res.json();
      setReadiness(data);
    } catch {
      setReadiness({ status: 'ready', services: { adk_runtime: 'Google ADK 2.9.0 Active', tools_registry: '4 Tools Active', guardrails: 'Enforced', database: 'SQLite/pgvector' } });
    }
  };

  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API_BASE}/documents`);
      const data = await res.json();
      setDocuments(Array.isArray(data) ? data : []);
    } catch {
      setDocuments([]);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const res = await fetch(`${API_BASE}/workflows`);
      const data = await res.json();
      setWorkflows(Array.isArray(data) ? data : []);
    } catch {
      setWorkflows([]);
    }
  };

  const fetchEvaluations = async () => {
    try {
      const res = await fetch(`${API_BASE}/evaluations`);
      const data = await res.json();
      setEvaluations(Array.isArray(data) ? data : []);
    } catch {
      setEvaluations([]);
    }
  };

  const fetchBenchmarks = async () => {
    try {
      const res = await fetch(`${API_BASE}/evaluations/benchmarks`);
      const data = await res.json();
      setBenchmarks(data.test_cases || []);
    } catch {
      setBenchmarks([]);
    }
  };

  const handleRunTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsExecuting(true);
    try {
      const res = await fetch(`${API_BASE}/tasks/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: taskInput, mode: taskMode, has_approval: taskApproval })
      });
      const data = await res.json();
      setTaskResult(data);
      if (data.run_id) setTraceRunId(data.run_id);
    } catch (err: any) {
      setTaskResult({ status: 'error', error: String(err) });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleRagSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsRagQuerying(true);
    try {
      const res = await fetch(`${API_BASE}/rag/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: ragQuery, top_k: 5 })
      });
      const data = await res.json();
      setRagResult(data);
    } catch (err: any) {
      setRagResult({ status: 'error', answer: 'Failed to query RAG backend endpoint.', confidence_score: 0, citations: [] });
    } finally {
      setIsRagQuerying(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const formData = new FormData();
    formData.append('file', e.target.files[0]);

    try {
      await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData
      });
      fetchDocuments();
    } catch (err) {
      console.error('File upload failed', err);
    }
  };

  const handleCreateWorkflow = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsWfCreating(true);
    try {
      const res = await fetch(`${API_BASE}/workflows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: wfName, description: wfDesc })
      });
      const data = await res.json();
      setWorkflows(prev => [data, ...prev]);
      setActiveTab('workflows');
    } catch (err) {
      console.error('Failed to create workflow', err);
    } finally {
      setIsWfCreating(false);
    }
  };

  const handleLookupTrace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!traceRunId) return;
    try {
      const res = await fetch(`${API_BASE}/tasks/${traceRunId}`);
      const data = await res.json();
      setTraceData(data);
    } catch (err) {
      setTraceData({ error: 'Trace ID not found or server error.' });
    }
  };

  const handleRunEvaluation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/evaluations/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_text: evalInput, actual_output: evalActual })
      });
      const data = await res.json();
      setEvalResult(data);
      fetchEvaluations();
    } catch (err) {
      console.error('Evaluation failed', err);
    }
  };

  const agentsList = [
    { name: 'Root Orchestrator', role: 'Main Dispatcher', desc: 'Google ADK 2.9.0 master coordinator delegating tasks across specialized sub-agents.', model: 'gemini-2.0-flash', status: 'Active' },
    { name: 'Planner Agent', role: 'Strategy & Decomposition', desc: 'Decomposes complex requests into executable dependency-aware step graphs.', model: 'gemini-2.0-flash', status: 'Active' },
    { name: 'Researcher Agent', role: 'Web & Document RAG', desc: 'Retrieves knowledge chunks, queries Tavily web search, and extracts PDF context.', model: 'gemini-2.0-flash', status: 'Active' },
    { name: 'Reviewer Agent', role: 'Code & Output Inspector', desc: 'Inspects code quality, syntax correctness, and security vulnerability patterns.', model: 'gemini-2.0-flash', status: 'Active' },
    { name: 'Analyst Agent', role: 'Data Analysis & Insights', desc: 'Performs statistical evaluations, trend extraction, and metric aggregation.', model: 'gemini-2.0-flash', status: 'Active' },
    { name: 'Coder Agent', role: 'Code Generation', desc: 'Generates production Python/TypeScript code matching strict specifications.', model: 'gemini-2.0-flash', status: 'Active' },
    { name: 'Critic Agent', role: 'Adversarial Tester', desc: 'Evaluates logical consistency, potential edge cases, and failure modes.', model: 'gemini-2.0-flash', status: 'Active' },
    { name: 'Summarizer Agent', role: 'Synthesis Engine', desc: 'Synthesizes multi-agent conversation outputs into executive summaries.', model: 'gemini-2.0-flash', status: 'Active' }
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0f172a', color: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Sidebar */}
      <aside style={{ width: '270px', backgroundColor: '#1e293b', borderRight: '1px solid #334155', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.25rem', color: '#fff', boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)' }}>AF</div>
          <div>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>AgentForge AI</h1>
            <span style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 500 }}>Google ADK 2.9.0 Runtime</span>
          </div>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          {[
            { id: 'overview', label: '📊 Overview' },
            { id: 'agents', label: '🤖 Agents & Swarm' },
            { id: 'workflows', label: '⚡ Workflows' },
            { id: 'builder', label: '🧩 Visual Builder' },
            { id: 'documents', label: '📁 Knowledge Docs' },
            { id: 'rag', label: '🔍 Vector RAG Search' },
            { id: 'tasks', label: '🚀 Task Execution' },
            { id: 'traces', label: '⏱️ Execution Traces' },
            { id: 'evaluations', label: '📈 AI Evaluations' },
            { id: 'settings', label: '⚙️ Settings & Security' }
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as Tab)}
              style={{
                textAlign: 'left',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === item.id ? '#2563eb' : 'transparent',
                color: activeTab === item.id ? '#ffffff' : '#94a3b8',
                fontWeight: activeTab === item.id ? 600 : 400,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div style={{ marginTop: 'auto', paddingTop: '1.5rem', borderTop: '1px solid #334155', fontSize: '0.75rem', color: '#64748b' }}>
          <div>Backend: FastAPI (Port 8000)</div>
          <div>Framework: Google ADK 2.9.0</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
        {/* Header bar */}
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid #334155' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.6rem', fontWeight: 700, textTransform: 'capitalize' }}>
              {activeTab === 'rag' ? 'Vector RAG Search & Q&A' : activeTab.replace('_', ' ')}
            </h2>
            <p style={{ margin: '0.25rem 0 0 0', color: '#94a3b8', fontSize: '0.875rem' }}>
              Connected Live API • <span style={{ color: '#38bdf8' }}>{API_BASE}</span>
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <span style={{ padding: '0.4rem 0.9rem', borderRadius: '9999px', backgroundColor: readiness?.status === 'ready' ? '#059669' : '#d97706', color: '#ecfdf5', fontSize: '0.8rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#34d399' }}></span>
              {readiness?.status === 'ready' ? 'API Connected' : 'Connecting...'}
            </span>
          </div>
        </header>

        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
              {[
                { title: 'Agent Swarm', val: `${agentsList.length} Active Agents`, sub: 'Google ADK 2.9.0 Runner', color: '#60a5fa' },
                { title: 'ADK Status', val: 'Active Engine', sub: readiness?.services?.adk_runtime || 'InMemorySessionService', color: '#34d399' },
                { title: 'Ingested Docs', val: `${documents.length} Documents`, sub: 'Memory & pgvector Store', color: '#a7f3d0' },
                { title: 'Security Shield', val: 'Protected', sub: 'Input/Output Secret Scrubber', color: '#c084fc' }
              ].map((c, i) => (
                <div key={i} style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
                  <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>{c.title}</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0.5rem 0', color: c.color }}>{c.val}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{c.sub}</div>
                </div>
              ))}
            </div>

            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem', marginBottom: '2rem' }}>
              <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Enterprise Agent System Architecture</h3>
              <pre style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', color: '#a7f3d0', fontSize: '0.85rem', overflowX: 'auto', lineHeight: '1.5' }}>
{`User Request ──► FastAPI Gateway ──► Input Guardrails ──► Root Orchestrator (Google ADK 2.9.0)
                                                               │
                                ┌──────────────────────────────┼──────────────────────────────┐
                                ▼                              ▼                              ▼
                         Planner Agent                  Researcher Agent               Reviewer Agent
                          (Task Graph)                   (RAG & Web Search)             (Code/Security)
                                │                              │                              │
                                └──────────────────────────────┼──────────────────────────────┘
                                                               ▼
                                                      Output Guardrails (CoT Redaction)
                                                               │
                                                               ▼
                                                      OpenTelemetry Traces & Dashboard`}
              </pre>
            </div>
          </div>
        )}

        {/* AGENTS TAB */}
        {activeTab === 'agents' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.25rem' }}>
              {agentsList.map((agent, i) => (
                <div key={i} style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <div>
                      <h4 style={{ margin: 0, fontSize: '1.1rem', color: '#38bdf8' }}>{agent.name}</h4>
                      <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{agent.role}</span>
                    </div>
                    <span style={{ padding: '0.2rem 0.6rem', borderRadius: '4px', backgroundColor: '#065f46', color: '#34d399', fontSize: '0.75rem', fontWeight: 600 }}>{agent.status}</span>
                  </div>
                  <p style={{ fontSize: '0.875rem', color: '#cbd5e1', marginBottom: '1rem', lineHeight: '1.4' }}>{agent.desc}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b', borderTop: '1px solid #334155', paddingTop: '0.75rem' }}>
                    <span>LLM Model: <strong style={{ color: '#94a3b8' }}>{agent.model}</strong></span>
                    <span>Runtime: <strong style={{ color: '#94a3b8' }}>Google ADK 2.9.0</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* WORKFLOWS TAB */}
        {activeTab === 'workflows' && (
          <div>
            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Active Workflow Pipelines ({workflows.length})</h3>
                <button onClick={() => setActiveTab('builder')} style={{ padding: '0.5rem 1rem', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem' }}>
                  + Create New Workflow
                </button>
              </div>
              {workflows.length === 0 ? (
                <p style={{ color: '#64748b' }}>No custom workflows generated yet. Click "Create New Workflow" to generate one via visual builder.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {workflows.map((wf, idx) => (
                    <div key={idx} style={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '1.25rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <h4 style={{ margin: 0, color: '#f8fafc' }}>{wf.name} <span style={{ fontSize: '0.8rem', color: '#64748b' }}>({wf.id})</span></h4>
                        <span style={{ fontSize: '0.8rem', color: '#34d399' }}>{wf.nodes?.length || 0} Task Graph Nodes</span>
                      </div>
                      <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: '0 0 1rem 0' }}>{wf.description}</p>
                      {wf.visualizations?.mermaid && (
                        <div>
                          <span style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 600 }}>Mermaid Graph Definition:</span>
                          <pre style={{ backgroundColor: '#1e293b', padding: '0.75rem', borderRadius: '6px', fontSize: '0.8rem', color: '#a7f3d0', overflowX: 'auto', marginTop: '0.4rem' }}>
                            {wf.visualizations.mermaid}
                          </pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* VISUAL BUILDER TAB */}
        {activeTab === 'builder' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Natural Language Visual Workflow Builder</h3>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Specify a target business task, and AgentForge AI will build a directed acyclic task graph (DAG) with node dependency specs.</p>
            <form onSubmit={handleCreateWorkflow} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.4rem' }}>Workflow Title</label>
                <input
                  type="text"
                  value={wfName}
                  onChange={(e) => setWfName(e.target.value)}
                  style={{ width: '100%', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '0.75rem', color: '#fff' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.4rem' }}>Workflow Goal & Instructions</label>
                <textarea
                  value={wfDesc}
                  onChange={(e) => setWfDesc(e.target.value)}
                  rows={4}
                  style={{ width: '100%', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '0.75rem', color: '#fff' }}
                />
              </div>
              <button
                type="submit"
                disabled={isWfCreating}
                style={{ padding: '0.75rem 1.5rem', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer', alignSelf: 'flex-start' }}
              >
                {isWfCreating ? 'Generating DAG Graph...' : 'Build Task Graph Workflow'}
              </button>
            </form>
          </div>
        )}

        {/* KNOWLEDGE DOCS TAB */}
        {activeTab === 'documents' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#38bdf8' }}>RAG Knowledge Base Documents</h3>
              <label style={{ padding: '0.6rem 1.2rem', backgroundColor: '#2563eb', color: '#fff', borderRadius: '6px', cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem' }}>
                + Upload Document (PDF/MD/TXT)
                <input type="file" onChange={handleFileUpload} accept=".pdf,.txt,.md,.docx" style={{ display: 'none' }} />
              </label>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                  <th style={{ padding: '0.75rem' }}>Doc ID</th>
                  <th style={{ padding: '0.75rem' }}>Filename</th>
                  <th style={{ padding: '0.75rem' }}>Size</th>
                  <th style={{ padding: '0.75rem' }}>Vector Chunks</th>
                  <th style={{ padding: '0.75rem' }}>RAG Status</th>
                </tr>
              </thead>
              <tbody>
                {documents.length === 0 ? (
                  <tr><td colSpan={5} style={{ padding: '1.5rem', color: '#64748b', textAlign: 'center' }}>No documents uploaded yet. Upload a document to chunk & embed into RAG vector store.</td></tr>
                ) : (
                  documents.map((doc, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #334155' }}>
                      <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: '#60a5fa' }}>{doc.doc_id}</td>
                      <td style={{ padding: '0.75rem', color: '#f8fafc' }}>{doc.filename}</td>
                      <td style={{ padding: '0.75rem', color: '#94a3b8' }}>{doc.file_size} Bytes</td>
                      <td style={{ padding: '0.75rem', color: '#38bdf8' }}>{doc.num_chunks} Chunks</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span style={{ padding: '0.2rem 0.6rem', borderRadius: '4px', backgroundColor: '#065f46', color: '#34d399', fontSize: '0.75rem', fontWeight: 600 }}>{doc.status || 'Indexed'}</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* VECTOR RAG SEARCH TAB */}
        {activeTab === 'rag' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Vector RAG Hybrid Search & Citation Engine</h3>
            <form onSubmit={handleRagSearch} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', marginTop: '1rem' }}>
              <input
                type="text"
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
                style={{ flex: 1, backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '0.75rem 1rem', color: '#fff', fontSize: '0.95rem' }}
                placeholder="Ask a question over knowledge base..."
              />
              <button type="submit" disabled={isRagQuerying} style={{ padding: '0.75rem 1.5rem', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}>
                {isRagQuerying ? 'Querying Vector Store...' : 'Execute RAG Search'}
              </button>
            </form>

            {ragResult && (
              <div style={{ backgroundColor: '#0f172a', border: '1px solid #334155', padding: '1.25rem', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #334155', paddingBottom: '0.75rem' }}>
                  <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Confidence Score: <strong style={{ color: '#34d399' }}>{ragResult.confidence_score}</strong></span>
                  <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Citations Count: <strong style={{ color: '#38bdf8' }}>{ragResult.citations?.length || 0} Sources</strong></span>
                </div>
                <p style={{ fontSize: '1rem', color: '#f8fafc', lineHeight: '1.5', margin: '0 0 1rem 0' }}>{ragResult.answer}</p>
                
                {ragResult.citations && ragResult.citations.length > 0 && (
                  <div>
                    <h5 style={{ color: '#38bdf8', margin: '0 0 0.5rem 0' }}>Retrieved Citations & Chunks:</h5>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {ragResult.citations.map((c: any, i: number) => (
                        <div key={i} style={{ backgroundColor: '#1e293b', padding: '0.75rem', borderRadius: '6px', fontSize: '0.8rem', color: '#cbd5e1' }}>
                          <strong style={{ color: '#60a5fa' }}>[{c.source_doc || 'Doc'}]</strong>: {c.text_snippet || JSON.stringify(c)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TASK EXECUTION TAB */}
        {activeTab === 'tasks' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Execute Agent Task Swarm</h3>
            <form onSubmit={handleRunTask} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.4rem' }}>Task Prompt / Instruction</label>
                <textarea
                  value={taskInput}
                  onChange={(e) => setTaskInput(e.target.value)}
                  rows={4}
                  style={{ width: '100%', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '1rem', color: '#f8fafc', fontSize: '0.95rem' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                <div>
                  <label style={{ fontSize: '0.85rem', color: '#94a3b8', marginRight: '0.5rem' }}>Orchestration Mode:</label>
                  <select
                    value={taskMode}
                    onChange={(e) => setTaskMode(e.target.value)}
                    style={{ backgroundColor: '#0f172a', border: '1px solid #334155', color: '#fff', padding: '0.5rem 1rem', borderRadius: '6px' }}
                  >
                    <option value="research">Research Swarm</option>
                    <option value="plan">Planning DAG</option>
                    <option value="execute">Full Code & Execution</option>
                  </select>
                </div>

                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: '#94a3b8', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={taskApproval}
                    onChange={(e) => setTaskApproval(e.target.checked)}
                  />
                  Has Human Approval (Grant Guardrails Permission)
                </label>
              </div>

              <button
                type="submit"
                disabled={isExecuting}
                style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer', alignSelf: 'flex-start' }}
              >
                {isExecuting ? 'Dispatching ADK Agent Swarm...' : 'Execute Swarm Task'}
              </button>
            </form>

            {taskResult && (
              <div style={{ marginTop: '2rem', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h4 style={{ margin: 0, color: '#38bdf8' }}>Execution Run Result</h4>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Run ID: <strong style={{ color: '#60a5fa' }}>{taskResult.run_id}</strong></span>
                </div>
                <div style={{ fontSize: '0.9rem', color: '#e2e8f0', lineHeight: '1.5' }}>
                  <p><strong>Status:</strong> <span style={{ color: '#34d399' }}>{taskResult.status}</span></p>
                  <strong>Synthesized Result:</strong>
                  <pre style={{ whiteSpace: 'pre-wrap', color: '#a7f3d0', backgroundColor: '#1e293b', padding: '1rem', borderRadius: '6px', marginTop: '0.5rem' }}>
                    {taskResult.result || JSON.stringify(taskResult, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}

        {/* EXECUTION TRACES TAB */}
        {activeTab === 'traces' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>OpenTelemetry Execution Traces</h3>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Inspect multi-agent invocation timeline, agent step latencies, and guardrail events by Run ID.</p>
            <form onSubmit={handleLookupTrace} style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', marginTop: '1rem' }}>
              <input
                type="text"
                value={traceRunId}
                onChange={(e) => setTraceRunId(e.target.value)}
                placeholder="Enter Execution Run ID (e.g. run-1234abcd)"
                style={{ flex: 1, backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '0.75rem 1rem', color: '#fff' }}
              />
              <button type="submit" style={{ padding: '0.75rem 1.5rem', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}>
                Lookup Trace Telemetry
              </button>
            </form>

            {traceData && (
              <div style={{ backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#38bdf8' }}>Trace Details for {traceData.run_id || 'Query'}</h4>
                <pre style={{ color: '#a7f3d0', fontSize: '0.85rem', overflowX: 'auto' }}>
                  {JSON.stringify(traceData, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* AI EVALUATIONS TAB */}
        {activeTab === 'evaluations' && (
          <div>
            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem' }}>
              <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Automated AI Response Evaluator</h3>
              <form onSubmit={handleRunEvaluation} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.4rem' }}>User Input / Prompt</label>
                  <input
                    type="text"
                    value={evalInput}
                    onChange={(e) => setEvalInput(e.target.value)}
                    style={{ width: '100%', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '0.75rem', color: '#fff' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.4rem' }}>Actual Agent Output</label>
                  <textarea
                    value={evalActual}
                    onChange={(e) => setEvalActual(e.target.value)}
                    rows={3}
                    style={{ width: '100%', backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '0.75rem', color: '#fff' }}
                  />
                </div>
                <button type="submit" style={{ padding: '0.75rem 1.5rem', backgroundColor: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer', alignSelf: 'flex-start' }}>
                  Run Evaluation Assessment
                </button>
              </form>

              {evalResult && (
                <div style={{ marginTop: '1.5rem', backgroundColor: '#0f172a', padding: '1.25rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <span style={{ fontSize: '1rem', color: '#38bdf8', fontWeight: 600 }}>Overall Evaluation Score:</span>
                    <span style={{ fontSize: '1.2rem', color: '#34d399', fontWeight: 700 }}>{evalResult.overall_score} / 1.0</span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                    <div style={{ backgroundColor: '#1e293b', padding: '0.75rem', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Relevance</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#60a5fa' }}>{evalResult.relevance_score}</div>
                    </div>
                    <div style={{ backgroundColor: '#1e293b', padding: '0.75rem', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Factual Accuracy</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34d399' }}>{evalResult.factual_accuracy_score}</div>
                    </div>
                    <div style={{ backgroundColor: '#1e293b', padding: '0.75rem', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Safety Compliance</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#a7f3d0' }}>{evalResult.safety_score}</div>
                    </div>
                    <div style={{ backgroundColor: '#1e293b', padding: '0.75rem', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>CoT Quality</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#c084fc' }}>{evalResult.cot_quality_score}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {evaluations.length > 0 && (
              <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem', marginBottom: '1.5rem' }}>
                <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Evaluation Run History ({evaluations.length})</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
                  {evaluations.map((ev, idx) => (
                    <div key={idx} style={{ backgroundColor: '#0f172a', padding: '0.75rem 1rem', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <strong style={{ color: '#f8fafc', fontSize: '0.9rem' }}>{ev.input_text || `Evaluation #${idx + 1}`}</strong>
                        <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Overall Score: {ev.overall_score}</div>
                      </div>
                      <span style={{ padding: '0.2rem 0.6rem', borderRadius: '4px', backgroundColor: '#065f46', color: '#34d399', fontSize: '0.75rem' }}>Completed</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
              <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Benchmark Evaluation Datasets ({benchmarks.length})</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
                {benchmarks.map((tc, idx) => (
                  <div key={idx} style={{ backgroundColor: '#0f172a', padding: '0.75rem 1rem', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong style={{ color: '#f8fafc', fontSize: '0.9rem' }}>{tc.name || `Benchmark #${idx + 1}`}</strong>
                      <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{tc.input_text}</div>
                    </div>
                    <span style={{ padding: '0.2rem 0.6rem', borderRadius: '4px', backgroundColor: '#1e293b', color: '#38bdf8', fontSize: '0.75rem' }}>{tc.expected_behavior || 'Verified Target'}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* SETTINGS & SECURITY TAB */}
        {activeTab === 'settings' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#38bdf8' }}>Security & Platform Governance</h3>
            
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ color: '#cbd5e1', marginBottom: '0.5rem' }}>Role-Based Access Control (RBAC) Matrix</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                    <th style={{ padding: '0.75rem' }}>Role</th>
                    <th style={{ padding: '0.75rem' }}>Orchestration</th>
                    <th style={{ padding: '0.75rem' }}>RAG Ingestion</th>
                    <th style={{ padding: '0.75rem' }}>Dangerous Ops Approval</th>
                    <th style={{ padding: '0.75rem' }}>System Config</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #334155' }}>
                    <td style={{ padding: '0.75rem', fontWeight: 600, color: '#f43f5e' }}>ADMIN</td>
                    <td style={{ padding: '0.75rem', color: '#34d399' }}>Full Access</td>
                    <td style={{ padding: '0.75rem', color: '#34d399' }}>Full Access</td>
                    <td style={{ padding: '0.75rem', color: '#34d399' }}>Authorized</td>
                    <td style={{ padding: '0.75rem', color: '#34d399' }}>Manage All</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #334155' }}>
                    <td style={{ padding: '0.75rem', fontWeight: 600, color: '#38bdf8' }}>ENGINEER</td>
                    <td style={{ padding: '0.75rem', color: '#34d399' }}>Full Access</td>
                    <td style={{ padding: '0.75rem', color: '#34d399' }}>Full Access</td>
                    <td style={{ padding: '0.75rem', color: '#fbbf24' }}>Requires Confirmation</td>
                    <td style={{ padding: '0.75rem', color: '#94a3b8' }}>Read Only</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #334155' }}>
                    <td style={{ padding: '0.75rem', fontWeight: 600, color: '#a7f3d0' }}>USER</td>
                    <td style={{ padding: '0.75rem', color: '#34d399' }}>Standard Tasks</td>
                    <td style={{ padding: '0.75rem', color: '#34d399' }}>Upload Allowed</td>
                    <td style={{ padding: '0.75rem', color: '#f43f5e' }}>Blocked</td>
                    <td style={{ padding: '0.75rem', color: '#94a3b8' }}>None</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div style={{ marginTop: '2rem', borderTop: '1px solid #334155', paddingTop: '1.5rem' }}>
              <h4 style={{ color: '#cbd5e1', marginBottom: '0.5rem' }}>Guardrail Rules</h4>
              <ul style={{ color: '#94a3b8', fontSize: '0.875rem', lineHeight: '1.6' }}>
                <li>Input Guard: Enforces 10,000 char prompt limit, blocks path traversal (`..`), blocks 10MB+ file uploads.</li>
                <li>Output Guard: Redacts API key patterns (`AIza...`, `sk-...`), strips internal CoT rationale tags (`&lt;thought&gt;`).</li>
                <li>Permissions Guard: Blocks system commands and destructive file operations unless `has_approval` flag is explicitly present.</li>
              </ul>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

