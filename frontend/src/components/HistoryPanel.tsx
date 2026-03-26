import { useState, useMemo } from 'react'
import { X, Trash2 } from 'lucide-react'
import { TASK_LABELS, STYLE_LABELS } from '../types'
import type { HistoryItem } from '../types'
import type { CustomStyleItem } from '../services/api'
import ConfirmDialog from './ConfirmDialog'
import './HistoryPanel.css'

const PAGE_SIZE = 8

interface Props {
  items: HistoryItem[]
  activeId: string
  onSelect: (item: HistoryItem) => void
  onDelete: (id: string) => void
  onClear: () => void
  customStyles?: CustomStyleItem[]
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function preview(text: string, max = 30): string {
  const line = text.replace(/\n/g, ' ').trim()
  return line.length > max ? line.slice(0, max) + '...' : line
}

export default function HistoryPanel({ items, activeId, onSelect, onDelete, onClear, customStyles = [] }: Props) {
  const [keyword, setKeyword] = useState('')
  const [showConfirm, setShowConfirm] = useState(false)
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)

  const filtered = useMemo(() => {
    const kw = keyword.trim().toLowerCase()
    if (!kw) return items
    return items
      .filter((item) =>
        item.content.toLowerCase().includes(kw) ||
        item.result.toLowerCase().includes(kw)
      )
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  }, [items, keyword])

  const visible = filtered.slice(0, visibleCount)
  const hasMore = filtered.length > visibleCount

  return (
    <div className="history-panel" role="complementary" aria-label="历史记录">
      <div className="history-header">
        <span>历史记录 ({items.length})</span>
        {items.length > 0 && (
          <button className="history-clear" onClick={() => setShowConfirm(true)} aria-label="清空所有历史记录">清空</button>
        )}
      </div>
      {items.length > 0 && (
        <div className="history-search">
          <input
            type="text"
            className="history-search-input"
            placeholder="搜索关键词..."
            value={keyword}
            onChange={(e) => { setKeyword(e.target.value); setVisibleCount(PAGE_SIZE) }}
          />
          {keyword && (
            <button className="history-search-clear" onClick={() => setKeyword('')} aria-label="清除搜索"><X size={14} /></button>
          )}
        </div>
      )}
      {filtered.length === 0 ? (
        <div className="history-empty">{keyword ? '没有匹配的记录' : '暂无记录'}</div>
      ) : (
        <ul className="history-list">
          {visible.map((item) => {
            const isPpt = item.style === 'ppt'
            const styleLabel = STYLE_LABELS[item.style]
              || customStyles.find((s) => s.slug === item.style)?.name
              || item.style
            return (
            <li
              key={item.id}
              className={`history-item ${item.id === activeId ? 'active' : ''} ${isPpt ? 'history-item-ppt' : ''}`}
              onClick={() => onSelect(item)}
            >
              <div className="history-item-top">
                <div className="history-tags">
                  <span className={`history-tag ${isPpt ? 'history-tag-ppt' : ''}`}>
                    {isPpt ? 'PPT' : TASK_LABELS[item.task_type]}
                  </span>
                  {item.style && item.style !== 'ppt' && (
                    <span className="history-tag history-tag-style">{styleLabel}</span>
                  )}
                </div>
                <span className="history-time">{formatTime(item.created_at)}</span>
              </div>
              <div className="history-preview">{preview(item.content)}</div>
              <button
                className="history-delete"
                onClick={(e) => { e.stopPropagation(); onDelete(item.id) }}
                title="删除"
                aria-label="删除此记录"
              >
                <Trash2 size={14} />
              </button>
            </li>
            )
          })}
        </ul>
      )}
      {hasMore && (
        <button
          className="history-more"
          onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
        >
          查看更多（还有 {filtered.length - visibleCount} 条）
        </button>
      )}
      {showConfirm && (
        <ConfirmDialog
          message="确定要清空所有历史记录吗？此操作不可恢复。"
          onConfirm={() => { setShowConfirm(false); onClear() }}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </div>
  )
}
