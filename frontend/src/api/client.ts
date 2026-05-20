import type { ChatMessage, ChatResponse, Skill, TopicCard } from './types'
export type { ChatMessage, ChatResponse, Skill, TopicCard }
export type { Source } from './types'

const BASE = 'http://localhost:8000/api'

const TOKEN_KEY = 'auth_token'

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

function authHeaders(): Record<string, string> {
  const token = tokenStore.get()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function post<T>(path: string, body: unknown, extraHeaders?: Record<string, string>): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...extraHeaders },
    body: JSON.stringify(body),
  })
  if (res.status === 401) { tokenStore.clear(); window.location.href = '/login' }
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { headers: authHeaders() })
  if (res.status === 401) { tokenStore.clear(); window.location.href = '/login' }
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function patch<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401) { tokenStore.clear(); window.location.href = '/login' }
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function del(path: string): Promise<void> {
  const res = await fetch(`${BASE}${path}`, { method: 'DELETE', headers: authHeaders() })
  if (res.status === 401) { tokenStore.clear(); window.location.href = '/login' }
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
}

export interface MarketStock { code: string; name: string; price: string; change: string; up: boolean }
export interface MarketBond { code: string; name: string; price: string; yield_: string; change: string }
export interface MarketFund { code: string; name: string; nav: string; change: string; type: string; up: boolean }
export interface MarketSnapshot { hot_stocks: MarketStock[]; bond_yields: MarketBond[]; fund_navs: MarketFund[] }

export const api = {
  async login(username: string, password: string): Promise<void> {
    const form = new URLSearchParams({ username, password })
    const res = await fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form.toString(),
    })
    if (!res.ok) throw new Error('用户名或密码错误')
    const data = await res.json()
    tokenStore.set(data.access_token)
  },

  logout(): void {
    tokenStore.clear()
    window.location.href = '/login'
  },

  me(): Promise<{ id: number; username: string }> {
    return get('/auth/me')
  },

  chat(messages: ChatMessage[], skillId?: string): Promise<ChatResponse> {
    return post('/chat', { messages, skill_id: skillId ?? null })
  },

  skills(category?: string): Promise<Skill[]> {
    const q = category ? `?category=${encodeURIComponent(category)}` : ''
    return get(`/skills${q}`)
  },

  cards(): Promise<TopicCard[]> {
    return get('/cards')
  },

  saveCard(id: string): Promise<TopicCard> {
    return patch(`/cards/${id}/save`)
  },

  deleteCard(id: string): Promise<void> {
    return del(`/cards/${id}`)
  },

  marketSnapshot(): Promise<MarketSnapshot> {
    return get('/market/snapshot')
  },
}
