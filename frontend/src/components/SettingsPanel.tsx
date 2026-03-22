import { useState } from 'react'
import './SettingsPanel.css'

export interface AppSettings {
  model: string
  temperature: number
  unsplashKey: string
}

const STORAGE_KEY = 'writing_settings'
const DEFAULTS: AppSettings = { model: '', temperature: 0.7, unsplashKey: '' }

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
          <label className="settings-field">
            <span className="settings-label">Model</span>
            <input
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="qwen3.5:9b (default)"
              className="settings-input"
            />
            <span className="settings-hint">Leave empty to use server default</span>
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
