import { useState, useEffect } from 'react'
import { fetchModels, healthCheck } from '../services/api'
import './SettingsPanel.css'

export interface AppSettings {
  model: string
  temperature: number
  unsplashKey: string
}

const STORAGE_KEY = 'writing_settings'
const DEFAULTS: AppSettings = { model: '', temperature: 0.7, unsplashKey: '' }

const PROVIDER_LABELS: Record<string, string> = {
  ollama: 'Ollama (本地)',
  openai: 'OpenAI',
  deepseek: 'DeepSeek',
  qwen: '通义千问',
}

export function loadSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...DEFAULTS }
    return { ...DEFAULTS, ...JSON.parse(raw) }
  } catch {
    return { ...DEFAULTS }
  }
}

export function saveSettings(s: AppSettings): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
}

interface Props {
  settings: AppSettings
  onSave: (s: AppSettings) => void
  onClose: () => void
}

export default function SettingsPanel({ settings, onSave, onClose }: Props) {
  const [model, setModel] = useState(settings.model)
  const [temperature, setTemperature] = useState(settings.temperature)
  const [unsplashKey, setUnsplashKey] = useState(settings.unsplashKey)
  const [modelList, setModelList] = useState<string[]>([])
  const [defaultModel, setDefaultModel] = useState('')
  const [modelsLoading, setModelsLoading] = useState(true)
  const [provider, setProvider] = useState('')
  const [availableProviders, setAvailableProviders] = useState<string[]>([])

  useEffect(() => {
    fetchModels().then((res) => {
      setModelList(res.models)
      setDefaultModel(res.default)
      setModelsLoading(false)
    })
    healthCheck().then((info) => {
      setProvider(info.provider || 'ollama')
      setAvailableProviders(info.availableProviders || ['ollama'])
    })
  }, [])

  const handleSave = () => {
    onSave({ model, temperature, unsplashKey })
    onClose()
  }

  const handleReset = () => {
    setModel(DEFAULTS.model)
    setTemperature(DEFAULTS.temperature)
    setUnsplashKey(DEFAULTS.unsplashKey)
  }

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <span className="settings-title">Settings</span>
          <button className="settings-close" onClick={onClose}>&times;</button>
        </div>

        <div className="settings-body">
          <div className="settings-field">
            <span className="settings-label">LLM Provider</span>
            <div className="settings-provider-info">
              <span className="settings-provider-badge">
                {PROVIDER_LABELS[provider] || provider}
              </span>
              {availableProviders.length > 1 && (
                <span className="settings-hint">
                  已配置: {availableProviders.map((p) => PROVIDER_LABELS[p] || p).join(', ')}
                </span>
              )}
            </div>
            <span className="settings-hint">
              通过环境变量 LLM_PROVIDER 切换。支持 ollama / openai / deepseek / qwen
            </span>
          </div>

          <label className="settings-field">
            <span className="settings-label">Model</span>
            {modelsLoading ? (
              <select className="settings-select" disabled>
                <option>Loading...</option>
              </select>
            ) : modelList.length > 0 ? (
              <select
                className="settings-select"
                value={model}
                onChange={(e) => setModel(e.target.value)}
              >
                <option value="">
                  {defaultModel ? `${defaultModel} (default)` : 'Server default'}
                </option>
                {modelList
                  .filter((m) => m !== defaultModel)
                  .map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
              </select>
            ) : (
              <input
                type="text"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="qwen3.5:9b (default)"
                className="settings-input"
              />
            )}
            <span className="settings-hint">
              {modelList.length > 0
                ? `${modelList.length} model(s) available`
                : 'Failed to fetch models, enter name manually'}
            </span>
          </label>

          <label className="settings-field">
            <span className="settings-label">
              Temperature: <strong>{temperature.toFixed(2)}</strong>
            </span>
            <input
              type="range"
              min="0"
              max="2"
              step="0.05"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="settings-slider"
            />
            <div className="settings-range-labels">
              <span>0 (precise)</span>
              <span>2 (creative)</span>
            </div>
          </label>

          <label className="settings-field">
            <span className="settings-label">Unsplash Access Key</span>
            <input
              type="password"
              value={unsplashKey}
              onChange={(e) => setUnsplashKey(e.target.value)}
              placeholder="PPT 配图用，留空则不配图"
              className="settings-input"
            />
            <span className="settings-hint">
              免费获取：<a href="https://unsplash.com/developers" target="_blank" rel="noreferrer">unsplash.com/developers</a>
            </span>
          </label>
        </div>

        <div className="settings-footer">
          <button className="settings-btn settings-btn-reset" onClick={handleReset}>Reset</button>
          <button className="settings-btn settings-btn-save" onClick={handleSave}>Save</button>
        </div>
      </div>
    </div>
  )
}
