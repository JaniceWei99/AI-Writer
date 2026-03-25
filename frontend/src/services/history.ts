import axios from 'axios'
import type { HistoryItem } from '../types'
import { getToken } from './auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '',
  timeout: 10_000,
})

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function getHistory(): Promise<HistoryItem[]> {
  const { data } = await api.get<HistoryItem[]>('/api/history')
  // 后端 id 是 number，前端 HistoryItem.id 是 string
  return data.map((item) => ({ ...item, id: String(item.id) }))
}

export async function addHistory(
  item: Omit<HistoryItem, 'id' | 'created_at'>,
): Promise<HistoryItem> {
  const { data } = await api.post<HistoryItem>('/api/history', item)
  return { ...data, id: String(data.id) }
}

export async function removeHistory(id: string): Promise<void> {
  await api.delete(`/api/history/${id}`)
}

export async function clearHistory(): Promise<void> {
  await api.delete('/api/history')
}
