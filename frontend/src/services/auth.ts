import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const authApi = axios.create({
  baseURL: API_BASE,
  timeout: 10_000,
})

const TOKEN_KEY = 'writing_auth_token'
const USER_KEY = 'writing_auth_user'

export interface AuthUser {
  user_id: number
  username: string
}

export interface AuthResult {
  token: string
  user_id: number
  username: string
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try { return JSON.parse(raw) } catch { return null }
}

export function saveAuth(result: AuthResult): void {
  localStorage.setItem(TOKEN_KEY, result.token)
  localStorage.setItem(USER_KEY, JSON.stringify({ user_id: result.user_id, username: result.username }))
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getAuthHeaders(): Record<string, string> {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function register(username: string, password: string): Promise<AuthResult> {
  const { data } = await authApi.post<AuthResult>('/api/auth/register', { username, password })
  saveAuth(data)
  return data
}

export async function login(username: string, password: string): Promise<AuthResult> {
  const { data } = await authApi.post<AuthResult>('/api/auth/login', { username, password })
  saveAuth(data)
  return data
}

export async function fetchMe(): Promise<AuthUser | null> {
  const token = getToken()
  if (!token) return null
  try {
    const { data } = await authApi.get<AuthUser>('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return data
  } catch {
    clearAuth()
    return null
  }
}
