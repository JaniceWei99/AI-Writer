import { useState, useEffect } from 'react'
import Markdown from 'react-markdown'
import { downloadDocx, downloadTxt, downloadMd, downloadPdf, downloadPptx } from '../services/api'
import { TaskType, PPT_TEMPLATE_OPTIONS } from '../types'
import './ResultPanel.css'

interface Props {
  result: string
  loading: boolean
  tokenCount: number
  error: string
  onRegenerate?: () => void
  onRetry?: () => void
  onResultChange?: (text: string) => void
  originalContent?: string
  taskType?: string
  style?: string
  unsplashKey?: string
}

export default function ResultPanel({
  result, loading, tokenCount, error,
  onRegenerate, onRetry, onResultChange,
  originalContent, taskType, style, unsplashKey,
}: Props) {
  const [exporting, setExporting] = useState(false)
  const [exportMsg, setExportMsg] = useState('')
  const [editing, setEditing] = useState(false)
  const [editText, setEditText] = useState('')
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [copyMsg, setCopyMsg] = useState('')
  const [showCompare, setShowCompare] = useState(false)
  const [pptTemplate, setPptTemplate] = useState('business')
  const [pptWithImages, setPptWithImages] = useState(false)

  const canCompare = !loading && result && originalContent &&
    (taskType === TaskType.POLISH || taskType === TaskType.TRANSLATE)

  useEffect(() => {
    if (!editing) setEditText(result)
  }, [result, editing])

  useEffect(() => {
    if (!showExportMenu) return
    const handler = () => setShowExportMenu(false)
    document.addEventListener('click', handler)
    return () => document.removeEventListener('click', handler)
  }, [showExportMenu])

  const handleToggleEdit = () => {
    if (editing) {
      onResultChange?.(editText)
      setEditing(false)
    } else {
      setEditText(result)
      setEditing(true)
    }
  }

  const handleCancelEdit = () => {
    setEditText(result)
    setEditing(false)
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
    setShowExportMenu(false)
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
        <div className="result-error">
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
          <p>选择任务类型，输入内容，点击「开始处理」查看结果</p>
        </div>
      </div>
    )
  }

  return (
    <div className="result-panel">
      <div className="result-header">
        <span className="result-title">生成结果</span>
        {tokenCount > 0 && (
          <span className="token-count">{tokenCount} tokens</span>
        )}
        {loading && <span className="generating">生成中...</span>}
        {canCompare && (
          <button
            className={`btn-compare ${showCompare ? 'active' : ''}`}
            onClick={() => setShowCompare(!showCompare)}
          >
            {showCompare ? '关闭对比' : '对比原文'}
          </button>
        )}
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
        <div className="result-content">
          {editing ? (
            <textarea
              className="result-edit-area"
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
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
            {copyMsg || '复制结果'}
          </button>

          {editing ? (
            <>
              <button className="btn btn-edit-save" onClick={handleToggleEdit}>保存编辑</button>
              <button className="btn btn-edit-cancel" onClick={handleCancelEdit}>取消</button>
            </>
          ) : (
            <button className="btn btn-edit" onClick={handleToggleEdit}>编辑</button>
          )}

          <div className="export-dropdown">
            <button
              className="btn btn-download"
              onClick={(e) => { e.stopPropagation(); setShowExportMenu(!showExportMenu) }}
              disabled={exporting}
            >
              {exporting ? '导出中...' : '导出 \u25be'}
            </button>
            {showExportMenu && (
              <div className="export-menu">
                <button onClick={() => handleExport('docx')}>Word (.docx)</button>
                <button onClick={() => handleExport('txt')}>纯文本 (.txt)</button>
                <button onClick={() => handleExport('md')}>Markdown (.md)</button>
                <button onClick={() => handleExport('pdf')}>PDF (.pdf)</button>
                <button onClick={() => handleExport('pptx')}>PPT (.pptx)</button>
              </div>
            )}
          </div>

          {style === 'ppt' && (
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
              {unsplashKey && (
                <label className="ppt-image-toggle">
                  <input
                    type="checkbox"
                    checked={pptWithImages}
                    onChange={(e) => setPptWithImages(e.target.checked)}
                  />
                  <span>配图</span>
                </label>
              )}
            </div>
          )}

          {onRegenerate && (
            <button className="btn btn-regenerate" onClick={onRegenerate}>换一个</button>
          )}

          {exportMsg && (
            <span className={`export-msg ${exportMsg === '下载成功' ? 'success' : 'fail'}`}>
              {exportMsg}
            </span>
          )}
        </div>
      )}
    </div>
  )
}
