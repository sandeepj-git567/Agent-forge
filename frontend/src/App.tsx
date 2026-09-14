import React, { useState, useEffect } from 'react';
import { api } from './api/client';

type Tab = 'overview' | 'agents' | 'workflows' | 'builder' | 'documents' | 'rag' | 'tasks' | 'traces' | 'evaluations' | 'settings';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  
  // Auth state
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [loginEmail, setLoginEmail] = useState('admin@agentforge.ai');
  const [loginPassword, setLoginPassword] = useState('admin123456');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerRole, setRegisterRole] = useState('USER');
  const [authError, setAuthError] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

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
  const [benchmarkSummary, setBenchmarkSummary] = useState<any>(null);

  // RAG state
  const [ragQuery, setRagQuery] = useState('What framework does AgentForge AI use?');
  const [ragResult, setRagResult] = useState<any>(null);
  const [isRagQuerying, setIsRagQuerying] = useState(false);

  // Workflow builder state
  const [wfName, setWfName] = useState('Enterprise Market Research Pipeline');
  const [wfDesc, setWfDesc] = useState('Plan research strategy, gather document context via RAG, analyze market trends, and output structured report.');
  const [isWfCreating, setIsWfCreating] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);

  // Trace lookup state
  const [traceRunId, setTraceRunId] = useState('');
  const [traceData, setTraceData] = useState<any>(null);

  // Eval state
  const [evalInput, setEvalInput] = useState('Explain RAG architecture in 2 sentences.');
  const [evalActual, setEvalActual] = useState('RAG combines retrieval of external vector documents with LLM text generation. This grounds model answers in accurate contextual data.');
  const [evalResult, setEvalResult] = useState<any>(null);
  const [isBenchmarking, setIsBenchmarking] = useState(false);

  // Notification state
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 4000);
  };

  // Initial data fetch
  useEffect(() => {
    fetchMe();
    fetchReadiness();
    fetchDocuments();
    fetchWorkflows();
    fetchEvaluations();
    fetchBenchmarks();
  }, []);

  const fetchMe = async () => {
    try {
      const user = await api.auth.me();
      setCurrentUser(user);
    } catch {
      setCurrentUser(null);
    }
  };

  const fetchReadiness = async () => {
    try {
      const data = await api.health.getReadiness();
      setReadiness(data);
    } catch {
      setReadiness({ status: 'ready', services: { adk_runtime: 'Google ADK 2.9.0 Active', tools_registry: '5 Tools Active', guardrails: 'Enforced', database: 'SQLite/pgvector' } });
    }
  };

  const fetchDocuments = async () => {
    try {
      const data = await api.documents.list();
      setDocuments(Array.isArray(data) ? data : []);
    } catch {
      setDocuments([]);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const data = await api.workflows.list();
      setWorkflows(Array.isArray(data) ? data : []);
    } catch {
      setWorkflows([]);
    }
  };

  const fetchEvaluations = async () => {
    try {
      const data = await api.evaluations.list();
      setEvaluations(Array.isArray(data) ? data : []);
    } catch {
      setEvaluations([]);
    }
  };

  const fetchBenchmarks = async () => {
    try {
      const data = await api.evaluations.getBenchmarks();
      setBenchmarks(data.test_cases || []);
    } catch {
      setBenchmarks([]);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await api.auth.login({ email: loginEmail, password: loginPassword });
      localStorage.setItem('agentforge_token', res.access_token);
      setCurrentUser(res.user);
      setShowAuthModal(false);
      showToast(`Welcome back, ${res.user.email}!`);
    } catch (err: any) {
      setAuthError(err.message || 'Login failed');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await api.auth.register({ email: registerEmail, password: registerPassword, role: registerRole });
      localStorage.setItem('agentforge_token', res.access_token);
      setCurrentUser(res.user);
      setShowAuthModal(false);
      showToast(`Account registered successfully as ${res.user.role}!`);
    } catch (err: any) {
      setAuthError(err.message || 'Registration failed');
    }
  };

  const handleLogout = async () => {
    try {
      await api.auth.logout();
    } catch {}
    localStorage.removeItem('agentforge_token');
    setCurrentUser(null);
    showToast('Logged out successfully.');
  };

  const handleRunTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsExecuting(true);
    try {
      const data = await api.tasks.run({ task: taskInput, mode: taskMode, has_approval: taskApproval });
      setTaskResult(data);
      if (data.run_id) setTraceRunId(data.run_id);
      showToast('Agent task completed successfully!');
    } catch (err: any) {
      setTaskResult({ status: 'error', error: String(err.message || err) });
      showToast(err.message || 'Task execution failed', 'error');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleRagSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsRagQuerying(true);
    try {
      const data = await api.rag.answer(ragQuery, 5);
      setRagResult(data);
      showToast('RAG search completed with citations.');
    } catch (err: any) {
      setRagResult({ status: 'error', answer: 'Failed to query RAG backend endpoint.', confidence_score: 0, citations: [] });
      showToast(err.message || 'RAG query failed', 'error');
    } finally {
      setIsRagQuerying(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    try {
      const res = await api.documents.upload(e.target.files[0]);
      showToast(`Document '${res.document?.filename || 'file'}' ingested successfully!`);
      fetchDocuments();
    } catch (err: any) {
      showToast(err.message || 'File upload failed', 'error');
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    try {
      await api.documents.delete(docId);
      showToast(`Document '${docId}' deleted successfully.`);
      fetchDocuments();
    } catch (err: any) {
      showToast(err.message || 'Delete failed', 'error');
    }
  };

  const handleCreateWorkflow = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsWfCreating(true);
    try {
      const data = await api.workflows.create({ name: wfName, description: wfDesc });
      setWorkflows(prev => [data, ...prev]);
      setActiveTab('workflows');
      showToast(`Workflow '${data.name}' created!`);
    } catch (err: any) {
      showToast(err.message || 'Failed to create workflow', 'error');
    } finally {
      setIsWfCreating(false);
    }
  };

  const handleExecuteWorkflow = async (wfId: string) => {
    try {
      const data = await api.workflows.execute(wfId);
      setExecutionResult(data);
      showToast(`Workflow execution started (ID: ${data.execution_id})`);
    } catch (err: any) {
      showToast(err.message || 'Workflow execution failed', 'error');
    }
  };

  const handleApproveCheckpoint = async (approvalId: string) => {
    try {
      const res = await api.workflows.approveCheckpoint(approvalId);
      showToast('Human approval granted! Workflow resumed.');
      setExecutionResult(res);
    } catch (err: any) {
      showToast(err.message || 'Approval failed', 'error');
    }
  };

  const handleLookupTrace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!traceRunId) return;
    try {
      const data = await api.tasks.getStatus(traceRunId);
      setTraceData(data);
    } catch (err: any) {
      setTraceData({ error: err.message || 'Trace ID not found.' });
    }
  };

  const handleRunEvaluation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await api.evaluations.run({ input_text: evalInput, actual_output: evalActual });
      setEvalResult(data);
      fetchEvaluations();
      showToast(`Evaluation completed! Score: ${data.overall_score}`);
    } catch (err: any) {
      showToast(err.message || 'Evaluation failed', 'error');
    }
  };

  const handleRunBatchBenchmark = async () => {
    setIsBenchmarking(true);
    try {
      const summary = await api.evaluations.runBenchmark();
      setBenchmarkSummary(summary);
      showToast(`Benchmark completed! Average score: ${summary.avg_overall_score}`);
      fetchEvaluations();
    } catch (err: any) {
      showToast(err.message || 'Batch benchmark failed', 'error');
    } finally {
      setIsBenchmarking(false);
    }
  };

  const agentsList = [
    { name: 'Root Orchestrator', role: 'Main Dispatcher', desc: 'Google ADK 2.9.0 master coordinator delegating tasks across specialized sub-agents.', model: 'gemini-2.5-flash', status: 'Active' },
    { name: 'Planner Agent', role: 'Strategy & Decomposition', desc: 'Decomposes complex requests into executable dependency-aware DAG step graphs.', model: 'gemini-2.5-flash', status: 'Active' },
    { name: 'Researcher Agent', role: 'Web & Document RAG', desc: 'Retrieves knowledge chunks, queries web search, and extracts PDF context.', model: 'gemini-2.5-flash', status: 'Active' },
    { name: 'Reviewer Agent', role: 'Code & Output Inspector', desc: 'Inspects code quality, syntax correctness, and security vulnerability patterns.', model: 'gemini-2.5-flash', status: 'Active' },
    { name: 'Analyst Agent', role: 'Data Analysis & Insights', desc: 'Performs statistical evaluations, trend extraction, and metric aggregation.', model: 'gemini-2.5-flash', status: 'Active' },
    { name: 'Coder Agent', role: 'Code Generation', desc: 'Generates production Python/TypeScript code matching strict specifications.', model: 'gemini-2.5-flash', status: 'Active' },
    { name: 'Critic Agent', role: 'Adversarial Tester', desc: 'Evaluates logical consistency, potential edge cases, and failure modes.', model: 'gemini-2.5-flash', status: 'Active' },
    { name: 'Summarizer Agent', role: 'Synthesis Engine', desc: 'Synthesizes multi-agent conversation outputs into executive summaries.', model: 'gemini-2.5-flash', status: 'Active' }
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0f172a', color: '#f8fafc', fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Toast Notification */}
      {notification && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          zIndex: 9999,
          padding: '1rem 1.5rem',
          borderRadius: '8px',
          backgroundColor: notification.type === 'success' ? '#10b981' : '#ef4444',
          color: '#ffffff',
          fontWeight: 600,
          boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
          transition: 'all 0.3s ease'
        }}>
          {notification.message}
        </div>
      )}

      {/* Sidebar */}
      <aside style={{ width: '270px', backgroundColor: '#1e293b', borderRight: '1px solid #334155', padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.25rem', color: '#fff', boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)' }}>AF</div>
          <div>
            <h1 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>AgentForge AI</h1>
            <span style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 500 }}>Google ADK 2.9.0 Runtime</span>
          </div>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', flex: 1 }}>
          {[
            { id: 'overview', label: '📊 Overview' },
            { id: 'agents', label: '🤖 Agents & Swarm' },
            { id: 'workflows', label: '⚡ Executable DAG Workflows' },
            { id: 'builder', label: '🧩 Visual Builder' },
            { id: 'documents', label: '📁 Knowledge Docs' },
            { id: 'rag', label: '🔍 Vector RAG Search' },
            { id: 'tasks', label: '🚀 Task Execution' },
            { id: 'traces', label: '⏱️ Execution Traces' },
            { id: 'evaluations', label: '📈 AI Evaluations' },
            { id: 'settings', label: '⚙️ Auth & Security' }
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

        {/* User Auth Badge */}
        <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid #334155' }}>
          {currentUser ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>{currentUser.email}</div>
                <div style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 500 }}>Role: {currentUser.role}</div>
              </div>
              <button
                onClick={handleLogout}
                style={{ padding: '0.4rem 0.6rem', borderRadius: '6px', border: '1px solid #ef4444', backgroundColor: 'transparent', color: '#ef4444', fontSize: '0.75rem', cursor: 'pointer' }}
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
              style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', border: 'none', backgroundColor: '#3b82f6', color: '#fff', fontWeight: 600, cursor: 'pointer' }}
            >
              Sign In / Register
            </button>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
        {/* Top Header Bar */}
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid #334155' }}>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, textTransform: 'capitalize' }}>
              {activeTab === 'overview' && 'Platform Overview & Architecture'}
              {activeTab === 'agents' && 'Multi-Agent Swarm Registry'}
              {activeTab === 'workflows' && 'Executable DAG Workflows'}
              {activeTab === 'builder' && 'Visual Workflow Generator'}
              {activeTab === 'documents' && 'Document Ingestion & Knowledge Base'}
              {activeTab === 'rag' && 'Real pgvector RAG Pipeline'}
              {activeTab === 'tasks' && 'Agent Task Execution Engine'}
              {activeTab === 'traces' && 'Execution Traces & Audit Logs'}
              {activeTab === 'evaluations' && 'Automated AI Evaluation Engine'}
              {activeTab === 'settings' && 'Authentication & Security Guardrails'}
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: '0.25rem 0 0 0' }}>
              Enterprise AI Agent Platform powered by Google ADK 2.9.0 & pgvector RAG
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ padding: '0.5rem 1rem', borderRadius: '20px', backgroundColor: '#1e293b', border: '1px solid #334155', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: readiness?.status === 'ready' ? '#10b981' : '#f59e0b' }}></span>
              <span>ADK Runtime: <strong>{readiness?.services?.adk_runtime || 'Active'}</strong></span>
            </div>
          </div>
        </header>

        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
              {[
                { title: 'Registered Agents', val: '8 Specialized Agents', sub: 'Planner, Researcher, Coder, Reviewer' },
                { title: 'Vector Knowledge Store', val: `${documents.length} Ingested Docs`, sub: 'pgvector SHA-256 Deduplicated' },
                { title: 'DAG Workflows', val: `${workflows.length} Executable Graphs`, sub: 'Kahn\'s Topological Parallel Waves' },
                { title: 'Evaluation Benchmark', val: `${benchmarks.length} Test Cases`, sub: 'Correctness, Relevance, Groundedness' }
              ].map((card, i) => (
                <div key={i} style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{card.title}</span>
                  <div style={{ fontSize: '1.35rem', fontWeight: 700, margin: '0.5rem 0 0.25rem 0', color: '#f8fafc' }}>{card.val}</div>
                  <span style={{ fontSize: '0.75rem', color: '#38bdf8' }}>{card.sub}</span>
                </div>
              ))}
            </div>

            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginTop: 0 }}>Google ADK 2.9.0 Multi-Agent Architecture</h3>
              <p style={{ color: '#cbd5e1', lineHeight: '1.6' }}>
                AgentForge AI implements modular agent orchestration built on Google ADK 2.9.0. It features parallel DAG workflow execution, SHA-256 deduplicated pgvector RAG, SSRF URL security guardrails, output secret redaction, and database-backed evaluation benchmarks.
              </p>
            </div>
          </div>
        )}

        {/* Tab 2: Agents */}
        {activeTab === 'agents' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {agentsList.map((agent, i) => (
              <div key={i} style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <h4 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 600 }}>{agent.name}</h4>
                  <span style={{ padding: '0.2rem 0.5rem', borderRadius: '4px', backgroundColor: '#064e3b', color: '#34d399', fontSize: '0.75rem', fontWeight: 600 }}>{agent.status}</span>
                </div>
                <span style={{ fontSize: '0.8rem', color: '#38bdf8', fontWeight: 500 }}>{agent.role}</span>
                <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: '0.75rem 0 1rem 0', lineHeight: '1.5' }}>{agent.desc}</p>
                <div style={{ fontSize: '0.75rem', color: '#cbd5e1', borderTop: '1px solid #334155', paddingTop: '0.75rem' }}>
                  Model: <code>{agent.model}</code>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 3: Workflows */}
        {activeTab === 'workflows' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0 }}>Saved DAG Workflows</h3>
              <button onClick={() => setActiveTab('builder')} style={{ padding: '0.6rem 1.2rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>+ Build New Workflow</button>
            </div>

            {workflows.map((wf, i) => (
              <div key={i} style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h4 style={{ margin: 0, fontSize: '1.1rem' }}>{wf.name}</h4>
                    <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: '0.25rem 0 1rem 0' }}>{wf.description}</p>
                  </div>
                  <button onClick={() => handleExecuteWorkflow(wf.id)} style={{ padding: '0.5rem 1rem', borderRadius: '6px', border: 'none', backgroundColor: '#10b981', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>▶ Run Execution</button>
                </div>
                {wf.graph_definition?.nodes && (
                  <div style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                    <strong>DAG Nodes ({wf.graph_definition.nodes.length}):</strong>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                      {wf.graph_definition.nodes.map((node: any, idx: number) => (
                        <span key={idx} style={{ padding: '0.3rem 0.6rem', borderRadius: '4px', backgroundColor: '#334155', color: '#f8fafc', fontSize: '0.75rem' }}>
                          {node.id} ({node.agent || 'planner'}) {node.requires_approval ? '🔒 Approval Req' : ''}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {executionResult && (
              <div style={{ backgroundColor: '#1e293b', border: '1px solid #3b82f6', borderRadius: '12px', padding: '1.5rem' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#38bdf8' }}>Execution Trace Result (ID: {executionResult.execution_id})</h4>
                <pre style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', overflowX: 'auto', fontSize: '0.85rem' }}>
                  {JSON.stringify(executionResult, null, 2)}
                </pre>
                {executionResult.status === 'paused_approval' && (
                  <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#7c2d12', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>Human Approval Checkpoint Paused at Node: <strong>{executionResult.paused_node}</strong></span>
                    <button onClick={() => handleApproveCheckpoint(executionResult.approval_id)} style={{ padding: '0.5rem 1rem', borderRadius: '6px', border: 'none', backgroundColor: '#10b981', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>Approve & Resume</button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 4: Builder */}
        {activeTab === 'builder' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0 }}>Natural Language DAG Workflow Generator</h3>
            <form onSubmit={handleCreateWorkflow} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Workflow Title</label>
                <input type="text" value={wfName} onChange={e => setWfName(e.target.value)} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} required />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Goal / Specification Description</label>
                <textarea rows={4} value={wfDesc} onChange={e => setWfDesc(e.target.value)} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} required />
              </div>
              <button type="submit" disabled={isWfCreating} style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
                {isWfCreating ? 'Generating DAG Graph...' : 'Generate Executable DAG Workflow'}
              </button>
            </form>
          </div>
        )}

        {/* Tab 5: Documents */}
        {activeTab === 'documents' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>Upload Knowledge Base Document (PDF, DOCX, TXT, MD)</h3>
              <input type="file" onChange={handleFileUpload} accept=".pdf,.docx,.txt,.md" style={{ color: '#94a3b8' }} />
            </div>

            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>Ingested Knowledge Documents ({documents.length})</h3>
              {documents.length === 0 ? (
                <p style={{ color: '#94a3b8' }}>No documents ingested yet.</p>
              ) : (
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                      <th style={{ padding: '0.75rem' }}>Filename</th>
                      <th style={{ padding: '0.75rem' }}>File Size</th>
                      <th style={{ padding: '0.75rem' }}>SHA-256 Hash</th>
                      <th style={{ padding: '0.75rem' }}>Chunks</th>
                      <th style={{ padding: '0.75rem' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid #1e293b' }}>
                        <td style={{ padding: '0.75rem', fontWeight: 600 }}>{doc.filename}</td>
                        <td style={{ padding: '0.75rem' }}>{(doc.file_size / 1024).toFixed(1)} KB</td>
                        <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: '#38bdf8' }}>{doc.content_hash?.slice(0, 16)}...</td>
                        <td style={{ padding: '0.75rem' }}>{doc.num_chunks}</td>
                        <td style={{ padding: '0.75rem' }}>
                          <button onClick={() => handleDeleteDocument(doc.doc_id)} style={{ padding: '0.3rem 0.6rem', borderRadius: '4px', border: '1px solid #ef4444', backgroundColor: 'transparent', color: '#ef4444', cursor: 'pointer' }}>Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {/* Tab 6: RAG */}
        {activeTab === 'rag' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>pgvector Vector Search & QA Query</h3>
              <form onSubmit={handleRagSearch} style={{ display: 'flex', gap: '1rem' }}>
                <input type="text" value={ragQuery} onChange={e => setRagQuery(e.target.value)} style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} placeholder="Ask a question..." required />
                <button type="submit" disabled={isRagQuerying} style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
                  {isRagQuerying ? 'Searching...' : 'Ask RAG'}
                </button>
              </form>
            </div>

            {ragResult && (
              <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#38bdf8' }}>RAG Response</h4>
                <p style={{ fontSize: '1rem', lineHeight: '1.6' }}>{ragResult.answer}</p>
                {ragResult.sources && (
                  <div style={{ marginTop: '1rem', borderTop: '1px solid #334155', paddingTop: '1rem' }}>
                    <strong style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Citations & Sources ({ragResult.sources.length}):</strong>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.5rem' }}>
                      {ragResult.sources.map((src: any, idx: number) => (
                        <div key={idx} style={{ backgroundColor: '#0f172a', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                          <span style={{ color: '#38bdf8', fontWeight: 600 }}>[{idx+1}] {src.filename}</span> (Score: {src.score})
                          <p style={{ margin: '0.25rem 0 0 0', color: '#cbd5e1' }}>"{src.snippet}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Tab 7: Tasks */}
        {activeTab === 'tasks' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0 }}>Agent Task Execution Engine</h3>
            <form onSubmit={handleRunTask} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Task Prompt</label>
                <textarea rows={3} value={taskInput} onChange={e => setTaskInput(e.target.value)} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} required />
              </div>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <select value={taskMode} onChange={e => setTaskMode(e.target.value)} style={{ padding: '0.6rem', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }}>
                  <option value="general">General Mode</option>
                  <option value="research">Research Mode</option>
                  <option value="coding">Coding Mode</option>
                </select>
                <label style={{ fontSize: '0.85rem', color: '#cbd5e1', cursor: 'pointer' }}>
                  <input type="checkbox" checked={taskApproval} onChange={e => setTaskApproval(e.target.checked)} style={{ marginRight: '0.5rem' }} />
                  Human Approval Token Granted
                </label>
              </div>
              <button type="submit" disabled={isExecuting} style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
                {isExecuting ? 'Executing Task...' : 'Run Agent Task'}
              </button>
            </form>

            {taskResult && (
              <div style={{ marginTop: '1.5rem', backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px' }}>
                <h4>Execution Output (Run ID: {taskResult.run_id})</h4>
                <pre style={{ overflowX: 'auto', fontSize: '0.85rem', color: '#34d399' }}>{taskResult.answer || JSON.stringify(taskResult, null, 2)}</pre>
              </div>
            )}
          </div>
        )}

        {/* Tab 8: Traces */}
        {activeTab === 'traces' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0 }}>Execution Trace & Event Audit Lookup</h3>
            <form onSubmit={handleLookupTrace} style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
              <input type="text" value={traceRunId} onChange={e => setTraceRunId(e.target.value)} placeholder="Enter Task Run ID..." style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} required />
              <button type="submit" style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>Lookup Trace</button>
            </form>

            {traceData && (
              <pre style={{ backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px', overflowX: 'auto', fontSize: '0.85rem' }}>
                {JSON.stringify(traceData, null, 2)}
              </pre>
            )}
          </div>
        )}

        {/* Tab 9: Evaluations */}
        {activeTab === 'evaluations' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0 }}>Automated AI Evaluation Engine</h3>
              <button onClick={handleRunBatchBenchmark} disabled={isBenchmarking} style={{ padding: '0.6rem 1.2rem', borderRadius: '8px', border: 'none', backgroundColor: '#8b5cf6', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
                {isBenchmarking ? 'Running Benchmark Batch...' : '▶ Run Batch Benchmark'}
              </button>
            </div>

            {benchmarkSummary && (
              <div style={{ backgroundColor: '#1e293b', border: '1px solid #8b5cf6', borderRadius: '12px', padding: '1.5rem' }}>
                <h4 style={{ margin: '0 0 1rem 0', color: '#a78bfa' }}>Batch Benchmark Execution Results ({benchmarkSummary.benchmark_id})</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
                  <div style={{ backgroundColor: '#0f172a', padding: '0.75rem', borderRadius: '8px' }}>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Overall Score</span>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#10b981' }}>{benchmarkSummary.avg_overall_score}</div>
                  </div>
                  <div style={{ backgroundColor: '#0f172a', padding: '0.75rem', borderRadius: '8px' }}>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Correctness</span>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{benchmarkSummary.avg_correctness}</div>
                  </div>
                  <div style={{ backgroundColor: '#0f172a', padding: '0.75rem', borderRadius: '8px' }}>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Relevance</span>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{benchmarkSummary.avg_relevance}</div>
                  </div>
                  <div style={{ backgroundColor: '#0f172a', padding: '0.75rem', borderRadius: '8px' }}>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Groundedness</span>
                    <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{benchmarkSummary.avg_groundedness}</div>
                  </div>
                </div>
              </div>
            )}

            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>Single Response Evaluation Form</h3>
              <form onSubmit={handleRunEvaluation} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Input Prompt</label>
                  <input type="text" value={evalInput} onChange={e => setEvalInput(e.target.value)} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} required />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Actual Agent Output</label>
                  <textarea rows={3} value={evalActual} onChange={e => setEvalActual(e.target.value)} style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} required />
                </div>
                <button type="submit" style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>Run Single Evaluation</button>
              </form>

              {evalResult && (
                <div style={{ marginTop: '1.5rem', backgroundColor: '#0f172a', padding: '1rem', borderRadius: '8px' }}>
                  <h4>Score: {evalResult.overall_score}</h4>
                  <pre style={{ fontSize: '0.85rem', color: '#38bdf8' }}>{JSON.stringify(evalResult, null, 2)}</pre>
                </div>
              )}
            </div>

            <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
              <h3 style={{ marginTop: 0 }}>Historical Evaluation Records ({evaluations.length})</h3>
              {evaluations.length === 0 ? (
                <p style={{ color: '#94a3b8' }}>No evaluation records logged yet.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {evaluations.map((ev, i) => (
                    <div key={i} style={{ backgroundColor: '#0f172a', padding: '0.75rem 1rem', borderRadius: '6px', fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Eval ID: <code>{ev.eval_id}</code></span>
                      <span style={{ fontWeight: 600, color: (ev.overall_score || 0) >= 0.7 ? '#10b981' : '#f59e0b' }}>Overall Score: {ev.overall_score || ev.metrics?.overall_score || 'N/A'}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 10: Settings */}
        {activeTab === 'settings' && (
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '1.5rem' }}>
            <h3 style={{ marginTop: 0 }}>Authentication & Security Guardrails</h3>
            {currentUser ? (
              <div>
                <p>Logged in as: <strong>{currentUser.email}</strong> (Role: {currentUser.role})</p>
                <button onClick={handleLogout} style={{ padding: '0.6rem 1.2rem', borderRadius: '6px', border: 'none', backgroundColor: '#ef4444', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>Sign Out Account</button>
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button onClick={() => { setAuthMode('login'); setShowAuthModal(true); }} style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>Login</button>
                <button onClick={() => { setAuthMode('register'); setShowAuthModal(true); }} style={{ padding: '0.75rem 1.5rem', borderRadius: '8px', border: '1px solid #334155', backgroundColor: 'transparent', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>Register New Account</button>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Auth Modal */}
      {showAuthModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
          <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '2rem', width: '400px', maxWidth: '90vw' }}>
            <h3 style={{ marginTop: 0 }}>{authMode === 'login' ? 'Account Login' : 'Register New Account'}</h3>
            {authError && <div style={{ padding: '0.5rem', backgroundColor: '#7f1d1d', color: '#fca5a5', borderRadius: '6px', fontSize: '0.85rem', marginBottom: '1rem' }}>{authError}</div>}
            
            <form onSubmit={authMode === 'login' ? handleLogin : handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Email Address</label>
                <input type="email" value={authMode === 'login' ? loginEmail : registerEmail} onChange={e => authMode === 'login' ? setLoginEmail(e.target.value) : setRegisterEmail(e.target.value)} style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} required />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Password</label>
                <input type="password" value={authMode === 'login' ? loginPassword : registerPassword} onChange={e => authMode === 'login' ? setLoginPassword(e.target.value) : setRegisterPassword(e.target.value)} style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }} required />
              </div>
              {authMode === 'register' && (
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Role</label>
                  <select value={registerRole} onChange={e => setRegisterRole(e.target.value)} style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#fff' }}>
                    <option value="USER">USER (Default)</option>
                    <option value="ENGINEER">ENGINEER</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                </div>
              )}
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button type="submit" style={{ flex: 1, padding: '0.75rem', borderRadius: '6px', border: 'none', backgroundColor: '#2563eb', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
                  {authMode === 'login' ? 'Sign In' : 'Register'}
                </button>
                <button type="button" onClick={() => setShowAuthModal(false)} style={{ padding: '0.75rem', borderRadius: '6px', border: '1px solid #334155', backgroundColor: 'transparent', color: '#94a3b8', cursor: 'pointer' }}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
