export type Contract = {
  id: string; name: string; contract_type: string; status: string;
  effective_date: string | null; expiration_date: string | null; created_at: string;
};
export type Risk = { id: string; contract_id: string; title: string; category: string; severity: string; explanation: string; business_impact: string | null; suggested_action: string | null; review_status: string; };
export type Obligation = { id: string; contract_id: string; responsible_party: string | null; description: string; due_date: string | null; due_date_text: string | null; priority: string; status: string; };

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';
const tokenKey = 'lexora.access_token';

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem(tokenKey);
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init.headers },
  });
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed (${response.status})`);
  return response.status === 204 ? (undefined as T) : response.json();
}

export const api = {
  login: (email: string, password: string) => request<{ access_token: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (full_name: string, email: string, password: string) => request('/auth/register', { method: 'POST', body: JSON.stringify({ full_name, email, password }) }),
  me: () => request<{ id: string; email: string; full_name: string }>('/auth/me'),
  contracts: () => request<{ items: Contract[]; total: number }>('/legal/contracts'),
  risks: (contractId: string) => request<Risk[]>(`/legal/contracts/${contractId}/risks`),
  reviewRisk: (riskId: string, status: string) => request<Risk>(`/legal/risks/${riskId}/review`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  obligations: () => request<Obligation[]>('/legal/obligations'),
  updateObligation: (id: string, status: string) => request<Obligation>(`/legal/obligations/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
  summary: (document_text: string, contract_type?: string) => request('/legal/summary', { method: 'POST', body: JSON.stringify({ document_text, contract_type }) }),
  clauses: (text: string) => request('/legal/clauses', { method: 'POST', body: JSON.stringify({ text }) }),
  workflow: (question: string, document_text: string) => request<{ answer: string; citations: string[]; evidence_valid: boolean; risks: Risk[]; obligations: Obligation[] }>('/legal/workflow', { method: 'POST', body: JSON.stringify({ task: 'question', question, document_text, chunks: [] }) }),
  compare: (original_text: string, revised_text: string) => request<{ changed: boolean; additions: number; deletions: number; changes: { change_type: string; original?: string; revised?: string }[] }>('/legal/compare', { method: 'POST', body: JSON.stringify({ original_text, revised_text }) }),
};

export const auth = { tokenKey, isSignedIn: () => Boolean(localStorage.getItem(tokenKey)), signOut: () => localStorage.removeItem(tokenKey) };
