import { useState } from 'react'
import { X, LogIn, LogOut } from 'lucide-react'
import { register, login, clearAuth } from '../services/auth'
import type { AuthUser } from '../services/auth'
import './AuthPanel.css'

interface Props {
  user: AuthUser | null
  onAuthChange: (user: AuthUser | null) => void
}

export default function AuthPanel({ user, onAuthChange }: Props) {
  const [showModal, setShowModal] = useState(false)
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!username.trim() || !password) return
    setLoading(true)
    setError('')
    try {
      const result = mode === 'register'
        ? await register(username.trim(), password)
        : await login(username.trim(), password)
      onAuthChange({ user_id: result.user_id, username: result.username })
      setShowModal(false)
      setUsername('')
      setPassword('')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } }
        setError(axiosErr.response?.data?.detail || '操作失败')
      } else {
        setError('网络错误')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    clearAuth()
    onAuthChange(null)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) handleSubmit()
  }

  // Logged-in view: show username + logout
  if (user) {
    return (
      <div className="auth-inline">
        <span className="auth-username" title={user.username}>{user.username}</span>
        <button className="btn-logout" onClick={handleLogout}><LogOut size={14} /> 退出</button>
      </div>
    )
  }

  // Logged-out view: login button
  return (
    <>
      <button className="btn-login" onClick={() => setShowModal(true)}><LogIn size={14} /> 登录</button>

      {showModal && (
        <div className="auth-overlay" onClick={() => setShowModal(false)} role="presentation">
          <div className="auth-modal" role="dialog" aria-modal="true" aria-labelledby="auth-title" onClick={(e) => e.stopPropagation()}>
            <div className="auth-modal-header">
              <h2 id="auth-title">{mode === 'login' ? '用户登录' : '注册账号'}</h2>
              <button className="auth-close" onClick={() => setShowModal(false)} aria-label="关闭"><X size={18} /></button>
            </div>

            <div className="auth-tabs">
              <button
                className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
                onClick={() => { setMode('login'); setError('') }}
              >
                登录
              </button>
              <button
                className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
                onClick={() => { setMode('register'); setError('') }}
              >
                注册
              </button>
            </div>

            <div className="auth-form">
              <label className="auth-field">
                <span>用户名</span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="请输入用户名"
                  autoFocus
                />
              </label>
              <label className="auth-field">
                <span>密码</span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={mode === 'register' ? '至少 4 个字符' : '请输入密码'}
                />
              </label>

              {error && <div className="auth-error" role="alert">{error}</div>}

              <button
                className="btn-auth-submit"
                onClick={handleSubmit}
                disabled={loading || !username.trim() || !password}
              >
                {loading ? '处理中...' : mode === 'login' ? '登录' : '注册'}
              </button>
            </div>

            <div className="auth-footer">
              {mode === 'login' ? (
                <span>还没有账号？<button className="auth-link" onClick={() => { setMode('register'); setError('') }}>立即注册</button></span>
              ) : (
                <span>已有账号？<button className="auth-link" onClick={() => { setMode('login'); setError('') }}>去登录</button></span>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
