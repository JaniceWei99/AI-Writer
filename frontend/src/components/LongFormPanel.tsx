import { useState, useRef, useCallback } from 'react'
import Markdown from 'react-markdown'
import './LongFormPanel.css'

interface Props {
  model?: string
  temperature?: number
  online: boolean | null
}

interface Chapter {
  title: string
  desc: string
  content: string
  status: 'pending' | 'generating' | 'done'
}

const API_BASE = import.meta.env.VITE_API_BASE || ''

function parseOutlineToChapters(outline: string): Chapter[] {
  const chapters: Chapter[] = []
  const lines = outline.split('\n')
  let currentTitle = ''
  let currentDesc = ''

  for (const line of lines) {
    const titleMatch = line.match(/^###\s*\d+[\.\u3001\uff0e]?\s*(.+)/)
    if (titleMatch) {
      if (currentTitle) {
        chapters.push({ title: currentTitle, desc: currentDesc.trim(), content: '', status: 'pending' })
      }
      currentTitle = titleMatch[1].trim()
      currentDesc = ''
    } else if (currentTitle && line.trim() && !line.startsWith('## ')) {
      currentDesc += line.trim() + ' '
    }
  }
  if (currentTitle) {
    chapters.push({ title: currentTitle, desc: currentDesc.trim(), content: '', status: 'pending' })
  }
  return chapters
}

async function streamFetch(
  url: string,
  body: object,
  onToken: (t: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const reader = res.body?.getReader()
  if (!reader) throw new Error('No reader')
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed.startsWith('data: ')) continue
      const payload = trimmed.slice(6)
      if (payload === '[DONE]') return
      try { onToken(JSON.parse(payload)) } catch { onToken(payload) }
    }
  }
}

type Phase = 'input' | 'outline-loading' | 'outline-review' | 'expanding' | 'done'

export default function LongFormPanel({ model, temperature, online }: Props) {
  const [phase, setPhase] = useState<Phase>('input')
  const [topic, setTopic] = useState('')
  const [style, setStyle] = useState('')
  const [outline, setOutline] = useState('')
  const [editOutline, setEditOutline] = useState('')
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [, setCurrentChapter] = useState(-1)
  const [fullArticle, setFullArticle] = useState('')
  const abortRef = useRef<AbortController | null>(null)

  const handleGenerateOutline = useCallback(async () => {
    if (!topic.trim()) return
    setPhase('outline-loading')
    setOutline('')
    const controller = new AbortController()
    abortRef.current = controller

    let text = ''
    try {
      await streamFetch(
        `${API_BASE}/api/writing/outline`,
        { content: topic, style, model: model || '', temperature },
        (token) => { text += token; setOutline(text) },
        controller.signal,
      )
      setEditOutline(text)
      setPhase('outline-review')
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') return
      setPhase('input')
    }
  }, [topic, style, model, temperature])

  const handleConfirmOutline = useCallback(async () => {
    const src = editOutline || outline
    const parsed = parseOutlineToChapters(src)
    if (parsed.length === 0) return
    setChapters(parsed)
    setPhase('expanding')
    setCurrentChapter(0)
    setFullArticle('')

    // Extract article title from outline
    const titleMatch = src.match(/^##\s*(.+)/m)
    let combined = titleMatch ? `# ${titleMatch[1]}\n\n` : ''

    const controller = new AbortController()
    abortRef.current = controller

    for (let i = 0; i < parsed.length; i++) {
      if (controller.signal.aborted) break
      setCurrentChapter(i)
      setChapters(prev => prev.map((c, idx) =>
        idx === i ? { ...c, status: 'generating' } : c
      ))

      let chapterText = ''
      try {
        await streamFetch(
          `${API_BASE}/api/writing/expand-chapter`,
          {
            outline: src,
            chapter_title: parsed[i].title,
            chapter_desc: parsed[i].desc,
            style,
            model: model || '',
            temperature,
          },
          (token) => {
            chapterText += token
            setChapters(prev => prev.map((c, idx) =>
              idx === i ? { ...c, content: chapterText } : c
            ))
            combined += token
            setFullArticle(combined)
          },
          controller.signal,
        )
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === 'AbortError') break
      }

      combined += '\n\n'
      setFullArticle(combined)
      setChapters(prev => prev.map((c, idx) =>
        idx === i ? { ...c, content: chapterText, status: 'done' } : c
      ))
    }
    setPhase('done')
  }, [editOutline, outline, style, model, temperature])

  const handleStop = () => {
    abortRef.current?.abort()
    abortRef.current = null
    if (phase === 'outline-loading') setPhase(outline ? 'outline-review' : 'input')
    else if (phase === 'expanding') setPhase('done')
  }

  const handleReset = () => {
    abortRef.current?.abort()
    setPhase('input')
    setOutline('')
    setEditOutline('')
    setChapters([])
    setCurrentChapter(-1)
    setFullArticle('')
  }

  const handleCopy = async () => {
    try { await navigator.clipboard.writeText(fullArticle) } catch {}
  }

  return (
    <div className="longform-panel">
      <div className="longform-header">
        <span className="longform-title">长文分章节写作</span>
        {phase !== 'input' && (
          <button className="btn btn-lf-reset" onClick={handleReset}>重新开始</button>
        )}
      </div>

      {/* Phase 1: Input */}
      {phase === 'input' && (
        <div className="longform-input-section">
          <textarea
            className="longform-topic-input"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="输入长文主题，例如：人工智能对教育行业的影响与未来趋势..."
            rows={3}
            aria-label="长文主题输入"
          />
          <div className="longform-input-actions">
            <select
              className="longform-style-select"
              value={style}
              onChange={(e) => setStyle(e.target.value)}
            >
              <option value="">默认风格</option>
              <option value="literary">文学</option>
              <option value="sh_gaokao">高考作文</option>
              <option value="zhihu">知乎风格</option>
              <option value="gongzhonghao">公众号</option>
            </select>
            <button
              className="btn btn-lf-generate"
              onClick={handleGenerateOutline}
              disabled={!topic.trim() || online === false}
            >
              生成大纲
            </button>
          </div>
        </div>
      )}

      {/* Phase 2: Outline loading */}
      {phase === 'outline-loading' && (
        <div className="longform-outline-section">
          <div className="longform-phase-label">正在生成大纲...</div>
          <div className="longform-outline-preview">
            <Markdown>{outline}</Markdown>
            <span className="cursor" />
          </div>
          <button className="btn btn-lf-stop" onClick={handleStop}>停止</button>
        </div>
      )}

      {/* Phase 3: Review outline */}
      {phase === 'outline-review' && (
        <div className="longform-outline-section">
          <div className="longform-phase-label">请确认或编辑大纲，确认后将逐章节展开</div>
          <textarea
            className="longform-outline-edit"
            value={editOutline}
            onChange={(e) => setEditOutline(e.target.value)}
            rows={12}
          />
          <div className="longform-review-actions">
            <button className="btn btn-lf-confirm" onClick={handleConfirmOutline}>
              确认大纲，开始写作
            </button>
            <button className="btn btn-lf-regen" onClick={handleGenerateOutline}>
              重新生成大纲
            </button>
          </div>
        </div>
      )}

      {/* Phase 4: Expanding chapters */}
      {(phase === 'expanding' || phase === 'done') && (
        <div className="longform-expand-section">
          <div className="longform-chapter-progress">
            {chapters.map((ch, i) => (
              <div key={i} className={`chapter-progress-item ${ch.status}`}>
                <span className="chapter-num">{i + 1}</span>
                <span className="chapter-name">{ch.title}</span>
                <span className="chapter-status-icon">
                  {ch.status === 'done' ? '\u2713' : ch.status === 'generating' ? '\u25cf' : '\u25cb'}
                </span>
              </div>
            ))}
          </div>

          <div className="longform-result" aria-live="polite">
            <Markdown>{fullArticle}</Markdown>
            {phase === 'expanding' && <span className="cursor" />}
          </div>

          <div className="longform-bottom-actions">
            {phase === 'expanding' && (
              <button className="btn btn-lf-stop" onClick={handleStop}>停止生成</button>
            )}
            {phase === 'done' && (
              <>
                <button className="btn btn-lf-copy" onClick={handleCopy}>复制全文</button>
                <span className="longform-stats">
                  共 {chapters.length} 章 · {fullArticle.length} 字
                </span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
