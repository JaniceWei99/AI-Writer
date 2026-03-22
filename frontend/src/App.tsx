import { useState, useRef, useEffect, useCallback } from 'react'
import WritingForm from './components/WritingForm'
import ResultPanel from './components/ResultPanel'
import HistoryPanel from './components/HistoryPanel'
import SettingsPanel, { loadSettings, saveSettings } from './components/SettingsPanel'
import type { AppSettings } from './components/SettingsPanel'
import { streamWriting, healthCheck } from './services/api'
import { getHistory, addHistory, removeHistory, clearHistory } from './services/history'
import type { WritingRequest, HistoryItem } from './types'
import './App.css'

type Theme = 'auto' | 'light' | 'dark'
const THEME_KEY = 'writing_theme'
const THEME_ICONS: Record<Theme, string> = { auto: 'A', light: '\u2600', dark: '\u263E' }
const THEME_LABELS: Record<Theme, string> = { auto: '\u8DDF\u968F\u7CFB\u7EDF', light: '\u4EAE\u8272', dark: '\u6697\u8272' }

function applyTheme(t: Theme) {
  const root = document.documentElement
  if (t === 'auto') root.removeAttribute('data-theme')
  else root.setAttribute('data-theme', t)
}

function App() {
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [tokenCount, setTokenCount] = useState(0)
  const [error, setError] = useState('')
  const [online, setOnline] = useState<boolean | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [activeId, setActiveId] = useState('')
  const abortRef = useRef<AbortController | null>(null)
  const lastReqRef = useRef<WritingRequest | null>(null)

  // Theme
  const [theme, setTheme] = useState<Theme>(() => {
    return (localStorage.getItem(THEME_KEY) as Theme) || 'auto'
  })

  // Settings
  const [settings, setSettings] = useState<AppSettings>(loadSettings)
  const [showSettings, setShowSettings] = useState(false)

  // Compare view: track the original content for polish/translate
  const [originalContent, setOriginalContent] = useState('')
  const [lastTaskType, setLastTaskType] = useState('')
  const [lastStyle, setLastStyle] = useState('')

  // Sidebar collapse (mobile)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Apply theme on mount and change
  useEffect(() => {
    applyTheme(theme)
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  useEffect(() => {
    healthCheck().then(setOnline)
    getHistory().then(setHistory).catch(() => {})
  }, [])

  // Global keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Esc: stop generation
      if (e.key === 'Escape' && loading) {
        e.preventDefault()
        handleStop()
      }
      // Ctrl+S: export (prevent browser save dialog)
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
      }
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [loading])

  const handleSubmit = useCallback(async (req: WritingRequest) => {
    // Merge settings into request
    const fullReq: WritingRequest = {
      ...req,
      model: settings.model || undefined,
      temperature: settings.temperature,
    }

    setResult('')
    setTokenCount(0)
    setError('')
    setLoading(true)
    setActiveId('')
    lastReqRef.current = fullReq
    setOriginalContent(req.content)
    setLastTaskType(req.task_type)
    setLastStyle(req.style)

    let fullText = ''
    let count = 0
    const controller = await streamWriting(
      fullReq,
      (token) => {
        count++
        fullText += token
        setResult((prev) => prev + token)
        setTokenCount(count)
      },
      () => {
        setLoading(false)
        if (fullText.trim() && lastReqRef.current) {
          addHistory({
            task_type: lastReqRef.current.task_type,
            content: lastReqRef.current.content,
            result: fullText,
            style: lastReqRef.current.style,
            token_count: count,
          }).then((entry) => {
            setActiveId(entry.id)
            getHistory().then(setHistory).catch(() => {})
          }).catch(() => {})
        }
      },
      (err) => {
        setError(err.message)
        setLoading(false)
      },
    )
    abortRef.current = controller
  }, [settings])

  const handleStop = () => {
    abortRef.current?.abort()
    abortRef.current = null
    setLoading(false)
  }

  const handleSelectHistory = useCallback((item: HistoryItem) => {
    setResult(item.result)
    setTokenCount(item.token_count)
    setError('')
    setActiveId(item.id)
    setOriginalContent(item.content)
    setLastTaskType(item.task_type)
  }, [])

  const handleDeleteHistory = useCallback(async (id: string) => {
    await removeHistory(id).catch(() => {})
    const items = await getHistory().catch(() => [] as HistoryItem[])
    setHistory(items)
    if (activeId === id) {
      setActiveId('')
      setResult('')
      setTokenCount(0)
    }
  }, [activeId])

  const handleClearHistory = useCallback(async () => {
    await clearHistory().catch(() => {})
    setHistory([])
    setActiveId('')
    setResult('')
    setTokenCount(0)
  }, [])

  const handleRegenerate = useCallback(() => {
    if (lastReqRef.current && !loading) {
      handleSubmit(lastReqRef.current)
    }
  }, [loading, handleSubmit])

  const handleRetry = useCallback(() => {
    if (lastReqRef.current && !loading) {
      handleSubmit(lastReqRef.current)
    }
  }, [loading, handleSubmit])

  const handleResultChange = useCallback((text: string) => {
    setResult(text)
  }, [])

  const handleSaveSettings = useCallback((s: AppSettings) => {
    setSettings(s)
    saveSettings(s)
  }, [])

  const cycleTheme = () => {
    setTheme((prev) => {
      const order: Theme[] = ['auto', 'light', 'dark']
      return order[(order.indexOf(prev) + 1) % order.length]
    })
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen((v) => !v)}
            title={sidebarOpen ? '收起侧边栏' : '展开侧边栏'}
          >
            &#9776;
          </button>
          <h1>AI 写作助手</h1>
        </div>
        <div className="header-actions">
          <button className="theme-toggle" onClick={cycleTheme} title={THEME_LABELS[theme]}>
            {THEME_ICONS[theme]}
          </button>
          <button className="settings-toggle" onClick={() => setShowSettings(true)} title="Settings">
            &#9881;
          </button>
          <span className={`status ${online === true ? 'online' : online === false ? 'offline' : ''}`}>
            {online === null ? '\u68C0\u6D4B\u4E2D...' : online ? '\u670D\u52A1\u5728\u7EBF' : '\u670D\u52A1\u79BB\u7EBF'}
          </span>
        </div>
      </header>

      <div className="app-body">
        <aside className={`app-sidebar ${sidebarOpen ? 'open' : ''}`}>
          <HistoryPanel
            items={history}
            activeId={activeId}
            onSelect={handleSelectHistory}
            onDelete={handleDeleteHistory}
            onClear={handleClearHistory}
          />
        </aside>

        <main className="app-main">
          <WritingForm
            onSubmit={handleSubmit}
            loading={loading}
            onStop={handleStop}
            online={online}
          />
          <ResultPanel
            result={result}
            loading={loading}
            tokenCount={tokenCount}
            error={error}
            onRegenerate={handleRegenerate}
            onRetry={handleRetry}
            onResultChange={handleResultChange}
            originalContent={originalContent}
            taskType={lastTaskType}
            style={lastStyle}
            unsplashKey={settings.unsplashKey}
          />
        </main>
      </div>

      <footer className="app-footer">
        <p>Powered by Ollama &middot; {settings.model || 'qwen3.5:9b'}</p>
      </footer>

      {showSettings && (
        <SettingsPanel
          settings={settings}
          onSave={handleSaveSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  )
}

export default App
