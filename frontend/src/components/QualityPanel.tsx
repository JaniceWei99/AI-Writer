import { useState, useEffect } from 'react'
import './QualityPanel.css'

interface QualityData {
  char_count: number
  word_count: number
  sentence_count: number
  paragraph_count: number
  avg_sentence_length: number
  unique_word_ratio: number
  paragraph_balance: number
  reading_time_minutes: number
  readability_score: number
  details: {
    sentence_length_score: number
    lexical_diversity_score: number
    paragraph_balance_score: number
    structure_score: number
  }
}

interface Props {
  content: string
}

function scoreColor(score: number): string {
  if (score >= 80) return 'var(--color-success)'
  if (score >= 60) return 'var(--color-warning)'
  if (score >= 40) return '#f97316'
  return 'var(--color-error)'
}

function scoreLabel(score: number): string {
  if (score >= 80) return '优秀'
  if (score >= 60) return '良好'
  if (score >= 40) return '一般'
  return '待改进'
}

export default function QualityPanel({ content }: Props) {
  const [data, setData] = useState<QualityData | null>(null)
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setData(null)
    setExpanded(false)
    setError('')
  }, [content])

  const handleAnalyze = async () => {
    if (!content.trim()) return
    if (data) {
      setExpanded(!expanded)
      return
    }
    setLoading(true)
    setError('')
    try {
      const API_BASE = import.meta.env.VITE_API_BASE || ''
      const res = await fetch(`${API_BASE}/api/analysis/quality`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const result: QualityData = await res.json()
      setData(result)
      setExpanded(true)
    } catch {
      setError('分析失败')
    } finally {
      setLoading(false)
    }
  }

  if (!content.trim()) return null

  return (
    <div className="quality-panel">
      <button
        className={`quality-toggle ${expanded ? 'active' : ''}`}
        onClick={handleAnalyze}
        disabled={loading}
        aria-expanded={expanded}
      >
        {loading ? '分析中...' : data ? (expanded ? '收起质量分析' : '展开质量分析') : '文本质量分析'}
        {data && !expanded && (
          <span className="quality-badge" style={{ color: scoreColor(data.readability_score) }}>
            {data.readability_score}分
          </span>
        )}
      </button>

      {error && <span className="quality-error" role="alert">{error}</span>}

      {expanded && data && (
        <div className="quality-content">
          {/* Main score */}
          <div className="quality-main-score">
            <div className="score-circle" style={{ borderColor: scoreColor(data.readability_score) }}>
              <span className="score-number" style={{ color: scoreColor(data.readability_score) }}>{data.readability_score}</span>
              <span className="score-label">{scoreLabel(data.readability_score)}</span>
            </div>
            <div className="score-reading-time">
              <span className="reading-time-value">{data.reading_time_minutes}</span>
              <span className="reading-time-unit">分钟阅读</span>
            </div>
          </div>

          {/* Stats row */}
          <div className="quality-stats">
            <div className="stat-item">
              <span className="stat-value">{data.char_count}</span>
              <span className="stat-label">字符</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{data.sentence_count}</span>
              <span className="stat-label">句子</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{data.paragraph_count}</span>
              <span className="stat-label">段落</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{data.avg_sentence_length}</span>
              <span className="stat-label">句均字数</span>
            </div>
          </div>

          {/* Sub-scores */}
          <div className="quality-subscores">
            <ScoreBar label="句长舒适度" score={data.details.sentence_length_score} />
            <ScoreBar label="用词丰富度" score={data.details.lexical_diversity_score} />
            <ScoreBar label="段落均衡度" score={data.details.paragraph_balance_score} />
            <ScoreBar label="结构合理性" score={data.details.structure_score} />
          </div>
        </div>
      )}
    </div>
  )
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  return (
    <div className="score-bar-row">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div
          className="score-bar-fill"
          style={{ width: `${score}%`, background: scoreColor(score) }}
        />
      </div>
      <span className="score-bar-value" style={{ color: scoreColor(score) }}>{score}</span>
    </div>
  )
}
