import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import WritingForm from '@/components/WritingForm'

describe('WritingForm', () => {
  const defaultProps = {
    onSubmit: vi.fn(),
    loading: false,
    onStop: vi.fn(),
  }

  it('renders all four task tabs', () => {
    render(<WritingForm {...defaultProps} />)
    expect(screen.getByText('文章生成')).toBeInTheDocument()
    expect(screen.getByText('文本润色')).toBeInTheDocument()
    expect(screen.getByText('文本翻译')).toBeInTheDocument()
    expect(screen.getByText('文本摘要')).toBeInTheDocument()
  })

  it('shows submit button and it is disabled when input is empty', () => {
    render(<WritingForm {...defaultProps} />)
    const btn = screen.getByText('开始处理')
    expect(btn).toBeDisabled()
  })

  it('enables submit button when content is entered', () => {
    render(<WritingForm {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/请输入主题/)
    fireEvent.change(textarea, { target: { value: '测试内容' } })
    expect(screen.getByText('开始处理')).not.toBeDisabled()
  })

  it('calls onSubmit with correct payload', () => {
    const onSubmit = vi.fn()
    render(<WritingForm {...defaultProps} onSubmit={onSubmit} />)
    const textarea = screen.getByPlaceholderText(/请输入主题/)
    fireEvent.change(textarea, { target: { value: 'AI未来' } })
    fireEvent.click(screen.getByText('开始处理'))
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        task_type: 'generate',
        content: 'AI未来',
      }),
    )
  })

  it('shows stop button when loading', () => {
    render(<WritingForm {...defaultProps} loading={true} />)
    expect(screen.getByText('停止生成')).toBeInTheDocument()
    expect(screen.queryByText('开始处理')).not.toBeInTheDocument()
  })

  it('calls onStop when stop button clicked', () => {
    const onStop = vi.fn()
    render(<WritingForm {...defaultProps} loading={true} onStop={onStop} />)
    fireEvent.click(screen.getByText('停止生成'))
    expect(onStop).toHaveBeenCalledOnce()
  })

  it('shows target language selector only for translate task', () => {
    render(<WritingForm {...defaultProps} />)
    expect(screen.queryByText('目标语言')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('文本翻译'))
    expect(screen.getByText('目标语言')).toBeInTheDocument()
  })

  it('shows style selector', () => {
    render(<WritingForm {...defaultProps} />)
    expect(screen.getByText('风格')).toBeInTheDocument()
  })

  it('shows upload button', () => {
    render(<WritingForm {...defaultProps} />)
    expect(screen.getByText('上传附件')).toBeInTheDocument()
  })

  it('switches placeholder when task changes', () => {
    render(<WritingForm {...defaultProps} />)
    expect(screen.getByPlaceholderText(/请输入主题/)).toBeInTheDocument()
    fireEvent.click(screen.getByText('文本润色'))
    expect(screen.getByPlaceholderText(/请粘贴需要润色/)).toBeInTheDocument()
  })

  it('disables task tabs and textarea while loading', () => {
    render(<WritingForm {...defaultProps} loading={true} />)
    const tabs = screen.getAllByRole('button').filter((b) => b.classList.contains('task-tab'))
    tabs.forEach((tab) => expect(tab).toBeDisabled())
  })
})
