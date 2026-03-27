import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import HistoryPanel from '@/components/HistoryPanel'
import type { HistoryItem } from '@/types'

const makeItem = (overrides: Partial<HistoryItem> = {}): HistoryItem => ({
  id: '1',
  task_type: 'generate',
  content: '测试内容',
  result: '测试结果',
  style: '',
  token_count: 10,
  created_at: '2025-01-15T10:30:00Z',
  ...overrides,
})

describe('HistoryPanel', () => {
  it('shows empty state when no items', () => {
    render(
      <HistoryPanel items={[]} activeId="" onSelect={vi.fn()} onDelete={vi.fn()} onClear={vi.fn()} />,
    )
    expect(screen.getByText('暂无记录')).toBeInTheDocument()
  })

  it('renders items with task label and preview', () => {
    const items = [makeItem({ id: '1', content: '人工智能' })]
    render(
      <HistoryPanel items={items} activeId="" onSelect={vi.fn()} onDelete={vi.fn()} onClear={vi.fn()} />,
    )
    expect(screen.getByText('文章生成')).toBeInTheDocument()
    expect(screen.getByText('人工智能')).toBeInTheDocument()
  })

  it('shows item count in header', () => {
    const items = [makeItem({ id: '1' }), makeItem({ id: '2' })]
    render(
      <HistoryPanel items={items} activeId="" onSelect={vi.fn()} onDelete={vi.fn()} onClear={vi.fn()} />,
    )
    expect(screen.getByText('历史记录 (2)')).toBeInTheDocument()
  })

  it('calls onSelect when item clicked', () => {
    const onSelect = vi.fn()
    const items = [makeItem()]
    render(
      <HistoryPanel items={items} activeId="" onSelect={onSelect} onDelete={vi.fn()} onClear={vi.fn()} />,
    )
    fireEvent.click(screen.getByText('测试内容'))
    expect(onSelect).toHaveBeenCalledWith(items[0])
  })

  it('calls onClear when clear button clicked and confirmed', () => {
    const onClear = vi.fn()
    const items = [makeItem()]
    render(
      <HistoryPanel items={items} activeId="" onSelect={vi.fn()} onDelete={vi.fn()} onClear={onClear} />,
    )
    fireEvent.click(screen.getByText('清空'))
    // ConfirmDialog appears — click the confirm button
    fireEvent.click(screen.getByText('确认'))
    expect(onClear).toHaveBeenCalledOnce()
  })

  it('calls onDelete without triggering onSelect', () => {
    const onSelect = vi.fn()
    const onDelete = vi.fn()
    const items = [makeItem({ id: 'abc' })]
    render(
      <HistoryPanel items={items} activeId="" onSelect={onSelect} onDelete={onDelete} onClear={vi.fn()} />,
    )
    fireEvent.click(screen.getByLabelText('删除此记录'))
    expect(onDelete).toHaveBeenCalledWith('abc')
    expect(onSelect).not.toHaveBeenCalled()
  })

  // --- Accessibility tests ---

  it('panel has role=complementary', () => {
    render(
      <HistoryPanel items={[]} activeId="" onSelect={vi.fn()} onDelete={vi.fn()} onClear={vi.fn()} />,
    )
    expect(screen.getByRole('complementary')).toBeInTheDocument()
  })

  it('panel has aria-label="历史记录"', () => {
    render(
      <HistoryPanel items={[]} activeId="" onSelect={vi.fn()} onDelete={vi.fn()} onClear={vi.fn()} />,
    )
    expect(screen.getByLabelText('历史记录')).toBeInTheDocument()
  })

  it('clear button has aria-label', () => {
    const items = [makeItem()]
    render(
      <HistoryPanel items={items} activeId="" onSelect={vi.fn()} onDelete={vi.fn()} onClear={vi.fn()} />,
    )
    expect(screen.getByLabelText('清空所有历史记录')).toBeInTheDocument()
  })

  it('delete button has aria-label="删除此记录"', () => {
    const items = [makeItem()]
    render(
      <HistoryPanel items={items} activeId="" onSelect={vi.fn()} onDelete={vi.fn()} onClear={vi.fn()} />,
    )
    expect(screen.getByLabelText('删除此记录')).toBeInTheDocument()
  })
})
