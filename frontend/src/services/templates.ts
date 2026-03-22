/**
 * Prompt 模板管理 —— localStorage 持久化
 */

export interface PromptTemplate {
  id: string
  name: string
  task_type: string
  content: string
  style: string
}

const STORAGE_KEY = 'writing_templates'

export function getTemplates(): PromptTemplate[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function addTemplate(t: Omit<PromptTemplate, 'id'>): PromptTemplate {
  const templates = getTemplates()
  const entry: PromptTemplate = {
    ...t,
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
  }
  templates.unshift(entry)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates))
  return entry
}

export function removeTemplate(id: string): void {
  const templates = getTemplates().filter((t) => t.id !== id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates))
}
