import { useState, useEffect } from 'react'
import {
  fetchCustomStyles,
  createCustomStyle,
  updateCustomStyle,
  deleteCustomStyle,
} from '../services/api'
import type { CustomStyleItem } from '../services/api'
import './StyleEditor.css'

interface Props {
  onClose: () => void
  onStylesChange: () => void
}

const TEMPLATE_HINT = '使用 {content} 作为用户输入的占位符。例如：\n\n你是一位微博文案专家。请根据以下主题撰写一条微博。\n\n主题：{content}\n\n请直接输出微博文案：'

export default function StyleEditor({ onClose, onStylesChange }: Props) {
  const [styles, setStyles] = useState<CustomStyleItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Form state
  const [editingId, setEditingId] = useState<number | null>(null)
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [description, setDescription] = useState('')
  const [promptTemplate, setPromptTemplate] = useState('')
  const [saving, setSaving] = useState(false)
  const [showForm, setShowForm] = useState(false)

  const loadStyles = async () => {
    setLoading(true)
    const data = await fetchCustomStyles()
    setStyles(data)
    setLoading(false)
  }

  useEffect(() => {
    loadStyles()
  }, [])

  const resetForm = () => {
    setEditingId(null)
    setName('')
    setSlug('')
    setDescription('')
    setPromptTemplate('')
    setError('')
  }

  const handleNew = () => {
    resetForm()
    setShowForm(true)
  }

  const handleEdit = (item: CustomStyleItem) => {
    setEditingId(item.id)
    setName(item.name)
    setSlug(item.slug)
    setDescription(item.description)
    setPromptTemplate(item.prompt_template)
    setError('')
    setShowForm(true)
  }

  const handleCancel = () => {
    resetForm()
    setShowForm(false)
  }

  const handleSave = async () => {
    if (!name.trim() || !slug.trim() || !promptTemplate.trim()) {
      setError('名称、标识符和 Prompt 模板不能为空')
      return
    }
    if (!promptTemplate.includes('{content}')) {
      setError('Prompt 模板必须包含 {content} 占位符')
      return
    }
    setSaving(true)
    setError('')
    try {
      if (editingId !== null) {
        await updateCustomStyle(editingId, {
          name: name.trim(),
          prompt_template: promptTemplate,
          description: description.trim(),
        })
      } else {
        await createCustomStyle({
          name: name.trim(),
          slug: slug.trim().toLowerCase(),
          prompt_template: promptTemplate,
          description: description.trim(),
        })
      }
      await loadStyles()
      onStylesChange()
      handleCancel()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '保存失败'
      // Try to extract detail from axios error
      const detail = (err as any)?.response?.data?.detail
      setError(detail || msg)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteCustomStyle(id)
      await loadStyles()
      onStylesChange()
      if (editingId === id) handleCancel()
    } catch {
      setError('删除失败')
    }
  }

  // Auto-generate slug from name (pinyin-like: just transliterate common patterns)
  const handleNameChange = (val: string) => {
    setName(val)
    if (editingId === null) {
      // Simple slug: lowercase, replace spaces/special with underscore
      const s = val
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9\u4e00-\u9fff]/g, '_')
        .replace(/[\u4e00-\u9fff]+/g, '') // remove CJK for slug
        .replace(/_+/g, '_')
        .replace(/^_|_$/g, '')
      if (s) setSlug(s)
    }
  }

  return (
    <div className="style-editor-overlay" onClick={onClose}>
      <div className="style-editor-panel" onClick={(e) => e.stopPropagation()}>
        <div className="style-editor-header">
          <span className="style-editor-title">自定义风格管理</span>
          <button className="style-editor-close" onClick={onClose}>&times;</button>
        </div>

        <div className="style-editor-body">
          {/* List of existing custom styles */}
          <div className="style-list">
            {loading ? (
              <div className="style-list-empty">加载中...</div>
            ) : styles.length === 0 ? (
              <div className="style-list-empty">暂无自定义风格，点击下方按钮创建</div>
            ) : (
              styles.map((item) => (
                <div key={item.id} className={`style-list-item ${editingId === item.id ? 'active' : ''}`}>
                  <div className="style-list-info" onClick={() => handleEdit(item)}>
                    <span className="style-list-name">{item.name}</span>
                    <span className="style-list-slug">{item.slug}</span>
                    {item.description && (
                      <span className="style-list-desc">{item.description}</span>
                    )}
                  </div>
                  <button
                    className="style-list-del"
                    onClick={() => handleDelete(item.id)}
                    title="删除"
                  >&times;</button>
                </div>
              ))
            )}
          </div>

          {!showForm && (
            <button className="btn style-btn-new" onClick={handleNew}>
              + 新建自定义风格
            </button>
          )}

          {/* Edit / Create form */}
          {showForm && (
            <div className="style-form">
              <div className="style-form-title">
                {editingId !== null ? '编辑风格' : '新建风格'}
              </div>

              <label className="style-form-field">
                <span>名称</span>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  placeholder="如：微博文案"
                  className="style-form-input"
                />
              </label>

              <label className="style-form-field">
                <span>标识符 (slug)</span>
                <input
                  type="text"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                  placeholder="如：weibo"
                  className="style-form-input"
                  disabled={editingId !== null}
                />
                <span className="style-form-hint">小写字母、数字、下划线，创建后不可修改</span>
              </label>

              <label className="style-form-field">
                <span>描述（可选）</span>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="简短描述这个风格的用途"
                  className="style-form-input"
                />
              </label>

              <label className="style-form-field">
                <span>Prompt 模板</span>
                <textarea
                  value={promptTemplate}
                  onChange={(e) => setPromptTemplate(e.target.value)}
                  placeholder={TEMPLATE_HINT}
                  className="style-form-textarea"
                  rows={10}
                />
                <span className="style-form-hint">
                  必须包含 {'{content}'} 占位符，运行时会替换为用户输入的内容
                </span>
              </label>

              {error && <div className="style-form-error">{error}</div>}

              <div className="style-form-actions">
                <button className="btn style-btn-cancel" onClick={handleCancel}>取消</button>
                <button
                  className="btn style-btn-save"
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? '保存中...' : '保存'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
