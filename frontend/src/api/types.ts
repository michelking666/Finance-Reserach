export interface Source {
  id: string
  title: string
  author?: string
  publisher?: string
  published_at?: string
  url?: string
  snippet?: string
  source_type: 'internal_report' | 'external_report' | 'external_consulting' | 'web'
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  skill_id?: string
}

export interface Metric {
  label: string
  value: string
  change: string
}

export interface TopicCard {
  id: string
  title: string
  subtitle?: string
  summary: string
  tags: string[]
  metrics: Metric[]
  bullets: string[]
  scenario?: string
  sources: Source[]
  created_at: string
  saved: boolean
}

export interface ChatResponse {
  message: ChatMessage
  sources: Source[]
  card?: TopicCard
  suggested_skills: string[]
}

export interface Skill {
  id: string
  name: string
  description: string
  category: string
  icon: string
  prompt_template: string
  sample_input?: string
  output_kind: 'text' | 'card' | 'table'
}
