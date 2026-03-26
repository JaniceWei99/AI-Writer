import { useState, useEffect } from 'react'
import { Copy, Edit3, Save, XCircle, RefreshCw, GitCompare, Sparkles, PenLine, Languages, MoreHorizontal } from 'lucide-react'
import Markdown from 'react-markdown'
import { downloadDocx, downloadTxt, downloadMd, downloadPdf, downloadPptx } from '../services/api'
import { TaskType, PPT_TEMPLATE_OPTIONS } from '../types'
import './ResultPanel.css'
import QualityPanel from './QualityPanel'

function countChars(text: string): number {
  return text.replace(/[#*_`~\[\]()>|{}\-\n\r\s]/g, '').length
}

interface Props {
  result: string
  loading: boolean
  tokenCount: number
  error: string
  onRegenerate?: () => void
  onRetry?: () => void
  onResultChange?: (text: string) => void
  onRefine?: (feedback: string) => void
  originalContent?: string
  taskType?: string
  style?: string
  unsplashKey?: string
  pptTemplate?: string
  pptWithImages?: boolean
  onQuickStart?: (taskType: string) => void
  wordCountTarget?: number
}

export default function ResultPanel({
  result, loading, tokenCount, error,
  onRegenerate, onRetry, onResultChange, onRefine,
  originalContent, taskType, style, unsplashKey,
  pptTemplate: pptTemplateProp, pptWithImages: pptWithImagesProp,
  onQuickStart, wordCountTarget,
}: Props) {
  const [exporting, setExporting] = useState(false)
  const [exportMsg, setExportMsg] = useState('')
  const [editing, setEditing] = useState(false)
  const [editText, setEditText] = useState('')
  const [showOverflow, setShowOverflow] = useState(false)
  const [copyMsg, setCopyMsg] = useState('')
  const [showCompare, setShowCompare] = useState(false)
  const [pptTemplate, setPptTemplate] = useState(pptTemplateProp || 'business')
  const [pptWithImages, setPptWithImages] = useState(pptWithImagesProp ?? true)
  const [refineText, setRefineText] = useState('')

  const isPpt = style === 'ppt'

  useEffect(() => {
    if (pptTemplateProp) setPptTemplate(pptTemplateProp)
  }, [pptTemplateProp])

  useEffect(() => {
    if (pptWithImagesProp !== undefined) setPptWithImages(pptWithImagesProp)
  }, [pptWithImagesProp])

  const canCompare = !loading && result && originalContent &&
    (taskType === TaskType.POLISH || taskType === TaskType.TRANSLATE)

  useEffect(() => {
    if (!editing) setEditText(result)
  }, [result, editing])

  useEffect(() => {
    if (!showOverflow) return
    const handler = () => setShowOverflow(false)
    document.addEventListener('click', handler)
    return () => document.removeEventListener('click', handler)
  }, [showOverflow])

  const handleToggleEdit = () => {
    if (editing) {
      onResultChange?.(editText)
      setEditing(false)
    } else {
      setEditText(result)
      setEditing(true)
    }
    setShowOverflow(false)
  }

  const handleCancelEdit = () => {
    setEditText(result)
    setEditing(false)
  }

  const handleRefineSubmit = () => {
    const text = refineText.trim()
    if (!text || !onRefine) return
    onRefine(text)
    setRefineText('')
  }

  const handleRefineKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleRefineSubmit()
    }
  }

  const currentContent = editing ? editText : result

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(currentContent)
      setCopyMsg('已复制')
      setTimeout(() => setCopyMsg(''), 2000)
    } catch {
      setCopyMsg('复制失败')
      setTimeout(() => setCopyMsg(''), 2000)
    }
  }

  const handleExport = async (format: 'docx' | 'txt' | 'md' | 'pdf' | 'pptx') => {
    setExporting(true)
    setExportMsg('')
    setShowOverflow(false)
    try {
      switch (format) {
        case 'docx': await downloadDocx(currentContent); break
        case 'txt':  downloadTxt(currentContent); break
        case 'md':   downloadMd(currentContent); break
        case 'pdf':  await downloadPdf(currentContent); break
        case 'pptx': await downloadPptx(currentContent, '', pptTemplate, pptWithImages, unsplashKey || ''); break
      }
      setExportMsg('下载成功')
      setTimeout(() => setExportMsg(''), 3000)
    } catch {
      setExportMsg('下载失败')
      setTimeout(() => setExportMsg(''), 3000)
    } finally {
      setExporting(false)
    }
  }

  if (error) {
    return (
      <div className="result-panel">
        <div className="result-error" role="alert">
          <strong>出错了</strong>
          <p>{error}</p>
          {onRetry && (
            <button className="btn btn-retry" onClick={onRetry}>重新尝试</button>
          )}
        </div>
      </div>
    )
  }

  if (!result && !loading) {
    return (
      <div className="result-panel">
        <div className="result-empty">
          <div className="empty-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="6" y="10" width="36" height="28" rx="4" stroke="currentColor" strokeWidth="1.5" opacity="0.3"/>
              <line x1="12" y1="18" x2="36" y2="18" stroke="currentColor" strokeWidth="1.5" opacity="0.2"/>
              <line x1="12" y1="24" x2="30" y2="24" stroke="currentColor" strokeWidth="1.5" opacity="0.2"/>
              <line x1="12" y1="30" x2="26" y2="30" stroke="currentColor" strokeWidth="1.5" opacity="0.2"/>
            </svg>
          </div>
          <p className="empty-title">开始创作</p>
          <p className="empty-subtitle">选择一个方式快速开始</p>
          {onQuickStart && (
            <div className="empty-quick-cards">
              <button className="empty-quick-card" onClick={() => onQuickStart('generate')}>
                <PenLine size={18} />
                <div className="quick-card-text">
                  <span className="quick-card-title">写一篇文章</span>
                  <span className="quick-card-desc">输入主题，AI 帮你生成</span>
                </div>
              </button>
              <button className="empty-quick-card" onClick={() => onQuickStart('polish')}>
                <Sparkles size={18} />
                <div className="quick-card-text">
                  <span className="quick-card-title">润色文本</span>
                  <span className="quick-card-desc">优化措辞，提升质量</span>
                </div>
              </button>
              <button className="empty-quick-card" onClick={() => onQuickStart('translate')}>
                <Languages size={18} />
                <div className="quick-card-text">
                  <span className="quick-card-title">翻译内容</span>
                  <span className="quick-card-desc">多语言互译</span>
                </div>
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  const charCount = countChars(result)
  const wordCountProgress = wordCountTarget && wordCountTarget > 0
    ? Math.min(100, (charCount / wordCountTarget) * 100)
    : 0

  return (
    <div className={`result-panel ${isPpt ? 'result-panel-ppt' : ''}`}>
      {loading && <div className="result-progress-bar"><div className="result-progress-fill" /></div>}
      <div className="result-header">
        <span className="result-title">生成结果</span>
        {isPpt ? (
          <span className="result-mode-badge ppt-badge">PPT 大纲</span>
        ) : style ? (
          <span className="result-mode-badge text-badge">文案</span>
        ) : null}
        {tokenCount > 0 && (
          <span className="token-count token-count-anim">{tokenCount} tokens</span>
        )}
        {loading && <span className="generating">生成中...</span>}
        <div className="result-header-end">
          {wordCountTarget && wordCountTarget > 0 ? (
            <div className="word-count-progress">
              <span className="word-count-text">{charCount} / {wordCountTarget} 字</span>
              <div className="word-count-bar">
                <div
                  className={`word-count-fill ${charCount >= wordCountTarget ? 'complete' : ''}`}
                  style={{ width: `${wordCountProgress}%` }}
                />
              </div>
            </div>
          ) : null}
          {canCompare && (
            <button
              className={`btn-compare ${showCompare ? 'active' : ''}`}
              onClick={() => setShowCompare(!showCompare)}
            >
              <GitCompare size={14} />
              {showCompare ? '关闭对比' : '对比原文'}
            </button>
          )}
        </div>
      </div>

      {showCompare && canCompare ? (
        <div className="compare-view">
          <div className="compare-pane">
            <div className="compare-label">原文</div>
            <div className="compare-content original">{originalContent}</div>
          </div>
          <div className="compare-pane">
            <div className="compare-label">结果</div>
            <div className="compare-content">
              <Markdown>{result}</Markdown>
            </div>
          </div>
        </div>
      ) : (
        <div className="result-content" aria-live="polite">
          {editing ? (
            <textarea
              className="result-edit-area"
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              aria-label="编辑生成结果"
            />
          ) : (
            <>
              <Markdown>{result}</Markdown>
              {loading && <span className="cursor" />}
            </>
          )}
        </div>
      )}

      {result && !loading && (
        <div className="result-actions">
          <button className="btn btn-copy" onClick={handleCopy}>
            <Copy size={14} />
            {copyMsg || '复制'}
          </button>

          {onRegenerate && (
            <button className="btn btn-regenerate" onClick={onRegenerate}><RefreshCw size={14} /> 换一个</button>
          )}

          {/* PPT mode: prominent PPTX export + template inline */}
          {isPpt && (
            <>
              <div className="ppt-options">
                <select
                  className="ppt-template-select"
                  value={pptTemplate}
                  onChange={(e) => setPptTemplate(e.target.value)}
                >
                  {PPT_TEMPLATE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
                <label className="ppt-image-toggle">
                  <input
                    type="checkbox"
                    checked={pptWithImages}
                    onChange={(e) => setPptWithImages(e.target.checked)}
                  />
                  <span>配图</span>
                </label>
              </div>
              <button
                className="btn btn-export-pptx"
                onClick={() => handleExport('pptx')}
                disabled={exporting}
              >
                {exporting ? '导出中...' : '导出 PPTX'}
              </button>
            </>
          )}

          {editing ? (
            <>
              <button className="btn btn-edit-save" onClick={handleToggleEdit}><Save size={14} /> 保存</button>
              <button className="btn btn-edit-cancel" onClick={handleCancelEdit}><XCircle size={14} /> 取消</button>
            </>
          ) : (
            <div className="overflow-dropdown">
              <button
                className="btn btn-overflow"
                onClick={(e) => { e.stopPropagation(); setShowOverflow(!showOverflow) }}
                title="更多操作"
              >
                <MoreHorizontal size={16} />
              </button>
              {showOverflow && (
                <div className="overflow-menu">
                  <button onClick={handleToggleEdit}><Edit3 size={14} /> 编辑结果</button>
                  <div className="overflow-divider" />
                  <button onClick={() => handleExport('docx')} disabled={exporting}>Word (.docx)</button>
                  <button onClick={() => handleExport('txt')} disabled={exporting}>纯文本 (.txt)</button>
                  <button onClick={() => handleExport('md')} disabled={exporting}>Markdown (.md)</button>
                  <button onClick={() => handleExport('pdf')} disabled={exporting}>PDF (.pdf)</button>
                  {!isPpt && (
                    <button onClick={() => handleExport('pptx')} disabled={exporting}>PPT (.pptx)</button>
                  )}
                </div>
              )}
            </div>
          )}

          {exportMsg && (
            <span className={`export-msg ${exportMsg === '下载成功' ? 'success' : 'fail'}`}>
              {exportMsg}
            </span>
          )}
        </div>
      )}
      {result && !loading && onRefine && (
        <div className="refine-bar">
          <div className="refine-suggestions">
            {['更简洁', '更正式', '扩写详细一些', '换个角度'].map((s) => (
              <button
                key={s}
                className="refine-suggestion-tag"
                onClick={() => { if (onRefine) onRefine(s) }}
              >
                {s}
              </button>
            ))}
          </div>
          <div className="refine-input-row">
            <textarea
              className="refine-input"
              value={refineText}
              onChange={(e) => setRefineText(e.target.value)}
              onKeyDown={handleRefineKeyDown}
              placeholder="或输入自定义修改意见..."
              rows={1}
              aria-label="输入修改意见"
            />
            <button
              className="btn btn-refine"
              onClick={handleRefineSubmit}
              disabled={!refineText.trim()}
            >
              <Sparkles size={14} />
              优化
            </button>
          </div>
        </div>
      )}
      {result && !loading && <QualityPanel content={result} />}
    </div>
  )
}
