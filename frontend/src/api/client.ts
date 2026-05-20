import type { ChatMessage, ChatResponse, Skill, TopicCard } from './types'
export type { ChatMessage, ChatResponse, Skill, TopicCard }
export type { Source } from './types'

const BASE = 'http://localhost:8000/api'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function patch<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function del(path: string): Promise<void> {
  const res = await fetch(`${BASE}${path}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
}

export interface MarketStock {
  code: string
  name: string
  price: string
  change: string
  up: boolean
}

export interface MarketBond {
  code: string
  name: string
  price: string
  yield_: string
  change: string
}

export interface MarketFund {
  code: string
  name: string
  nav: string
  change: string
  type: string
  up: boolean
}

export interface MarketSnapshot {
  hot_stocks: MarketStock[]
  bond_yields: MarketBond[]
  fund_navs: MarketFund[]
}

export const api = {
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
    return patch(`/cards/${id}`)
  },

  deleteCard(id: string): Promise<void> {
    return del(`/cards/${id}`)
  },

  marketSnapshot(): Promise<MarketSnapshot> {
    return get('/market/snapshot')
  },
}
