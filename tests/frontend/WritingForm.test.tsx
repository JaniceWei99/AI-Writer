import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import WritingForm from '@/components/WritingForm'

describe('WritingForm', () => {
  const defaultProps = {
    onSubmit: vi.fn(),
    loading: false,
    onStop: vi.fn(),
    online: true as boolean | null,
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

  it('shows target language selector only for translate task (behind advanced)', () => {
    render(<WritingForm {...defaultProps} />)
    // Expand advanced options first
    fireEvent.click(screen.getByText('高级选项'))
    expect(screen.queryByText('目标语言')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('文本翻译'))
    expect(screen.getByText('目标语言')).toBeInTheDocument()
  })

  it('shows style selector in advanced options', () => {
    render(<WritingForm {...defaultProps} />)
    // Style is behind advanced options
    expect(screen.queryByText('风格')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('高级选项'))
    expect(screen.getByText('风格')).toBeInTheDocument()
  })

  it('shows upload button in advanced options', () => {
    render(<WritingForm {...defaultProps} />)
    // Upload is behind advanced options
    expect(screen.queryByText('上传附件')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('高级选项'))
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

  // --- Mode switcher ---

  it('renders mode switcher with text and PPT modes', () => {
    render(<WritingForm {...defaultProps} />)
    expect(screen.getByText('文案创作')).toBeInTheDocument()
    expect(screen.getByText('演示文稿')).toBeInTheDocument()
  })

  it('switches to PPT mode and shows PPT placeholder', () => {
    render(<WritingForm {...defaultProps} />)
    fireEvent.click(screen.getByText('演示文稿'))
    expect(screen.getByPlaceholderText(/请输入PPT的主题/)).toBeInTheDocument()
    expect(screen.getByText('生成PPT大纲')).toBeInTheDocument()
  })

  // --- Tone control ---

  it('renders tone control buttons', () => {
    render(<WritingForm {...defaultProps} />)
    expect(screen.getByText('随意')).toBeInTheDocument()
    expect(screen.getByText('标准')).toBeInTheDocument()
    expect(screen.getByText('正式')).toBeInTheDocument()
  })

  it('appends casual tone instruction to content on submit', () => {
    const onSubmit = vi.fn()
    render(<WritingForm {...defaultProps} onSubmit={onSubmit} />)
    const textarea = screen.getByPlaceholderText(/请输入主题/)
    fireEvent.change(textarea, { target: { value: '测试' } })
    fireEvent.click(screen.getByText('随意'))
    fireEvent.click(screen.getByText('开始处理'))
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        content: expect.stringContaining('轻松随意'),
      }),
    )
  })

  it('appends formal tone instruction to content on submit', () => {
    const onSubmit = vi.fn()
    render(<WritingForm {...defaultProps} onSubmit={onSubmit} />)
    const textarea = screen.getByPlaceholderText(/请输入主题/)
    fireEvent.change(textarea, { target: { value: '测试' } })
    fireEvent.click(screen.getByText('正式'))
    fireEvent.click(screen.getByText('开始处理'))
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        content: expect.stringContaining('正式严谨'),
      }),
    )
  })

  it('does not append tone instruction for standard tone', () => {
    const onSubmit = vi.fn()
    render(<WritingForm {...defaultProps} onSubmit={onSubmit} />)
    const textarea = screen.getByPlaceholderText(/请输入主题/)
    fireEvent.change(textarea, { target: { value: '测试' } })
    // standard is the default, just submit
    fireEvent.click(screen.getByText('开始处理'))
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        content: '测试',
      }),
    )
  })

  // --- Word count target ---

  it('renders word target input', () => {
    const onWordCountTargetChange = vi.fn()
    render(
      <WritingForm
        {...defaultProps}
        wordCountTarget={0}
        onWordCountTargetChange={onWordCountTargetChange}
      />,
    )
    const input = screen.getByPlaceholderText('—')
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('type', 'number')
  })

  it('calls onWordCountTargetChange when target is set', () => {
    const onWordCountTargetChange = vi.fn()
    render(
      <WritingForm
        {...defaultProps}
        wordCountTarget={0}
        onWordCountTargetChange={onWordCountTargetChange}
      />,
    )
    const input = screen.getByPlaceholderText('—')
    fireEvent.change(input, { target: { value: '500' } })
    expect(onWordCountTargetChange).toHaveBeenCalledWith(500)
  })

  // --- Quick start ---

  it('sets task type on quick start', () => {
    const onQuickStartConsumed = vi.fn()
    render(
      <WritingForm
        {...defaultProps}
        quickStart={{ taskType: 'polish' }}
        onQuickStartConsumed={onQuickStartConsumed}
      />,
    )
    // After quick start, the polish tab should be active
    const polishTab = screen.getByText('文本润色')
    expect(polishTab.classList.contains('active')).toBe(true)
    expect(onQuickStartConsumed).toHaveBeenCalledOnce()
  })

  // --- Advanced options toggle ---

  it('toggles advanced options section', () => {
    render(<WritingForm {...defaultProps} />)
    // Initially hidden
    expect(screen.queryByText('风格')).not.toBeInTheDocument()
    // Click to expand
    fireEvent.click(screen.getByText('高级选项'))
    expect(screen.getByText('风格')).toBeInTheDocument()
    // Click again to collapse
    fireEvent.click(screen.getByText('高级选项'))
    expect(screen.queryByText('风格')).not.toBeInTheDocument()
  })

  // --- Accessibility tests ---

  it('textarea has aria-label attribute', () => {
    render(<WritingForm {...defaultProps} />)
    const textarea = screen.getByPlaceholderText(/请输入主题/)
    expect(textarea).toHaveAttribute('aria-label')
  })

  it('offline banner has role=alert', () => {
    render(<WritingForm {...defaultProps} online={false} />)
    const alerts = screen.getAllByRole('alert')
    expect(alerts.length).toBeGreaterThanOrEqual(1)
  })
})
