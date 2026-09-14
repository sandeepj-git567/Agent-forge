/**
 * AgentForge AI — Synchronized Typed API Client
 */

const getBaseUrl = (): string => {
  if (typeof window !== 'undefined' && window.location.origin) {
    if (window.location.port === '5173') {
      return 'http://localhost:8000/api/v1';
    }
    return `${window.location.origin}/api/v1`;
  }
  return 'http://localhost:8000/api/v1';
};

export const API_BASE = getBaseUrl();

export interface ApiOptions {
  headers?: Record<string, string>;
  params?: Record<string, any>;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('agentforge_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.error || errJson.message || `HTTP ${response.status}`;
    } catch {
      errorDetail = `HTTP Error ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Authentication
  auth: {
    register: (data: any) => request<any>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data: any) => request<any>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    logout: () => request<any>('/auth/logout', { method: 'POST' }),
    me: () => request<any>('/auth/me'),
    changePassword: (data: any) => request<any>('/auth/change-password', { method: 'POST', body: JSON.stringify(data) }),
  },

  // Health
  health: {
    getHealth: () => request<any>('/health'),
    getReadiness: () => request<any>('/health/ready'),
    getConfig: () => request<any>('/health/config'),
  },

  // Tasks
  tasks: {
    run: (payload: any) => request<any>('/tasks/run', { method: 'POST', body: JSON.stringify(payload) }),
    getStatus: (runId: string) => request<any>(`/tasks/${runId}`),
    cancel: (runId: string) => request<any>(`/tasks/${runId}/cancel`, { method: 'POST' }),
  },

  // Documents
  documents: {
    upload: async (file: File): Promise<any> => {
      const token = localStorage.getItem('agentforge_token');
      const formData = new FormData();
      formData.append('file', file);
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }
      return res.json();
    },
    list: () => request<any[]>('/documents'),
    get: (id: string) => request<any>(`/documents/${id}`),
    delete: (id: string) => request<any>(`/documents/${id}`, { method: 'DELETE' }),
  },

  // RAG Pipeline
  rag: {
    search: (query: string, topK: number = 3) => request<any>('/rag/search', { method: 'POST', body: JSON.stringify({ query, top_k: topK }) }),
    ask: (question: string, topK: number = 3) => request<any>('/rag/ask', { method: 'POST', body: JSON.stringify({ question, top_k: topK }) }),
    answer: (question: string, topK: number = 3) => request<any>('/rag/answer', { method: 'POST', body: JSON.stringify({ question, top_k: topK }) }),
  },

  // Workflows
  workflows: {
    create: (data: { name: string; description: string; graph_definition?: any }) => request<any>('/workflows', { method: 'POST', body: JSON.stringify(data) }),
    list: () => request<any[]>('/workflows'),
    get: (id: string) => request<any>(`/workflows/${id}`),
    visualize: (id: string) => request<any>(`/workflows/${id}/visualize`),
    execute: (id: string, inputs: any = {}) => request<any>(`/workflows/${id}/execute`, { method: 'POST', body: JSON.stringify({ inputs }) }),
    getExecution: (executionId: string) => request<any>(`/workflows/executions/${executionId}`),
    approveCheckpoint: (approvalId: string) => request<any>(`/workflows/approvals/${approvalId}/approve`, { method: 'POST' }),
    rejectCheckpoint: (approvalId: string) => request<any>(`/workflows/approvals/${approvalId}/reject`, { method: 'POST' }),
  },

  // Evaluations
  evaluations: {
    run: (payload: { input_text: string; actual_output: string; expected_output?: string }) => request<any>('/evaluations/run', { method: 'POST', body: JSON.stringify(payload) }),
    runBenchmark: () => request<any>('/evaluations/benchmark/run', { method: 'POST' }),
    list: () => request<any[]>('/evaluations'),
    getBenchmarks: () => request<any>('/evaluations/benchmarks'),
  },
};
