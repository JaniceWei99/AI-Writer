import { useState, useRef } from 'react'
import {
  TaskType,
  TASK_LABELS,
  TASK_PLACEHOLDERS,
  STYLE_OPTIONS,
  LANG_OPTIONS,
} from '../types'
import type { WritingRequest } from '../types'
import { uploadFile } from '../services/api'
import { getTemplates, addTemplate, removeTemplate } from '../services/templates'
import type { PromptTemplate } from '../services/templates'
import './WritingForm.css'

interface Props {
  onSubmit: (req: WritingRequest) => void
  loading: boolean
  onStop: () => void
  online: boolean | null
}

const ACCEPT_TYPES = '.pdf,.docx,.doc,.txt,.md,.csv,.json,.xml,.html,.htm'

export default function WritingForm({ onSubmit, loading, onStop, online }: Props) {
  const [taskType, setTaskType] = useState<TaskType>(TaskType.GENERATE)
  const [content, setContent] = useState('')
  const [style, setStyle] = useState('')
  const [targetLang, setTargetLang] = useState('英文')
  const [attachmentText, setAttachmentText] = useState('')
  const [attachmentName, setAttachmentName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Template management
  const [templates, setTemplates] = useState<PromptTemplate[]>(getTemplates)
  const [showTemplates, setShowTemplates] = useState(false)
  const [saveName, setSaveName] = useState('')
  const [showSave, setShowSave] = useState(false)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setUploadError('')
    try {
      const result = await uploadFile(file)
      setAttachmentText(result.text)
      setAttachmentName(result.filename)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '文件上传失败'
      setUploadError(msg)
      setAttachmentText('')
      setAttachmentName('')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleRemoveFile = () => {
    setAttachmentText('')
    setAttachmentName('')
    setUploadError('')
  }

  const handleSubmit = () => {
    if (!content.trim()) return
    onSubmit({
      task_type: taskType,
      content: content.trim(),
      style,
      target_lang: targetLang,
      attachment_text: attachmentText,
    })
  }

  // Ctrl+Enter to submit
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !loading && content.trim()) {
      e.preventDefault()
      handleSubmit()
    }
  }

  // Template operations
  const handleLoadTemplate = (t: PromptTemplate) => {
    setTaskType(t.task_type as TaskType)
    setContent(t.content)
    setStyle(t.style)
    setShowTemplates(false)
  }

  const handleSaveTemplate = () => {
    if (!saveName.trim() || !content.trim()) return
    addTemplate({
      name: saveName.trim(),
      task_type: taskType,
      content,
      style,
    })
    setTemplates(getTemplates())
    setSaveName('')
    setShowSave(false)
  }

  const handleDeleteTemplate = (id: string) => {
    removeTemplate(id)
    setTemplates(getTemplates())
  }

  return (
    <div className="writing-form">
      <div className="task-tabs">
        {Object.values(TaskType).map((t) => (
          <button
            key={t}
            className={`task-tab ${taskType === t ? 'active' : ''}`}
            onClick={() => setTaskType(t)}
            disabled={loading}
          >
            {TASK_LABELS[t]}
          </button>
        ))}
      </div>

      <textarea
        className="content-input"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={TASK_PLACEHOLDERS[taskType]}
        rows={8}
        disabled={loading}
      />
      <div className="content-counter">
        <span>{content.length} 字符</span>
        <span className="shortcut-hint">Ctrl+Enter 提交</span>
      </div>

      <div className="attachment-row">
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPT_TYPES}
          onChange={handleFileChange}
          disabled={loading || uploading}
          className="file-input-hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className={`btn btn-upload ${loading || uploading ? 'disabled' : ''}`}>
          {uploading ? '解析中...' : '上传附件'}
        </label>
        <span className="attachment-hint">支持 PDF、Word、TXT 等文件作为参考资料</span>

        {attachmentName && (
          <span className="attachment-tag">
            <span className="attachment-name">{attachmentName}</span>
            <button className="attachment-remove" onClick={handleRemoveFile} disabled={loading} title="移除附件">&times;</button>
          </span>
        )}

        {uploadError && <span className="attachment-error">{uploadError}</span>}
      </div>

      <div className="options-row">
        <label className="option">
          <span>风格</span>
          <select value={style} onChange={(e) => setStyle(e.target.value)} disabled={loading}>
            {STYLE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </label>

        {taskType === TaskType.TRANSLATE && (
          <label className="option">
            <span>目标语言</span>
            <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)} disabled={loading}>
              {LANG_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </label>
        )}

        {/* Template buttons */}
        <div className="template-group">
          <div className="template-dropdown-wrap">
            <button
              className="btn btn-template"
              onClick={(e) => { e.stopPropagation(); setShowTemplates(!showTemplates); setShowSave(false) }}
              disabled={loading}
            >
              模板 &#9662;
            </button>
            {showTemplates && (
              <div className="template-dropdown">
                {templates.length === 0 ? (
                  <div className="template-empty">暂无保存的模板</div>
                ) : (
                  templates.map((t) => (
                    <div key={t.id} className="template-item">
                      <button className="template-load" onClick={() => handleLoadTemplate(t)}>
                        <span className="template-name">{t.name}</span>
                        <span className="template-type">{TASK_LABELS[t.task_type as TaskType]}</span>
                      </button>
                      <button className="template-del" onClick={() => handleDeleteTemplate(t.id)}>&times;</button>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
          <button
            className="btn btn-template-save"
            onClick={() => { setShowSave(!showSave); setShowTemplates(false) }}
            disabled={loading || !content.trim()}
            title="保存当前内容为模板"
          >
            存为模板
          </button>
          {showSave && (
            <div className="template-save-form">
              <input
                type="text"
                className="template-save-input"
                placeholder="模板名称..."
                value={saveName}
                onChange={(e) => setSaveName(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleSaveTemplate() }}
                autoFocus
              />
              <button className="btn btn-template-confirm" onClick={handleSaveTemplate} disabled={!saveName.trim()}>
                保存
              </button>
            </div>
          )}
        </div>

        <div className="option-spacer" />

        {loading ? (
          <button className="btn btn-stop" onClick={onStop}>
            停止生成
          </button>
        ) : (
          <button
            className="btn btn-submit"
            onClick={handleSubmit}
            disabled={!content.trim() || online === false}
            title={online === false ? '服务离线，无法提交' : ''}
          >
            开始处理
          </button>
        )}
      </div>

      {online === false && (
        <div className="offline-banner">
          Ollama 服务未连接，请确认已启动 Ollama 并运行模型后刷新页面。
        </div>
      )}
    </div>
  )
}
