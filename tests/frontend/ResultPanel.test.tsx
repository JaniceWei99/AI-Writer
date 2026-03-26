import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ResultPanel from '@/components/ResultPanel'

describe('ResultPanel', () => {
  const defaultProps = {
    result: '',
    loading: false,
    tokenCount: 0,
    error: '',
  }

  it('shows empty state with "开始创作" when no result and not loading', () => {
    render(<ResultPanel {...defaultProps} />)
    expect(screen.getByText('开始创作')).toBeInTheDocument()
  })

  it('shows error message', () => {
    render(<ResultPanel {...defaultProps} error="连接失败" />)
    expect(screen.getByText('出错了')).toBeInTheDocument()
    expect(screen.getByText('连接失败')).toBeInTheDocument()
  })

  it('renders markdown result', () => {
    render(<ResultPanel {...defaultProps} result="**bold text**" tokenCount={10} />)
    expect(screen.getByText('bold text')).toBeInTheDocument()
    expect(screen.getByText('10 tokens')).toBeInTheDocument()
  })

  it('shows generating indicator while loading', () => {
    render(<ResultPanel {...defaultProps} result="partial" loading={true} tokenCount={3} />)
    expect(screen.getByText('生成中...')).toBeInTheDocument()
  })

  it('shows copy button when result is ready', () => {
    render(<ResultPanel {...defaultProps} result="some result" tokenCount={5} />)
    expect(screen.getByText('复制')).toBeInTheDocument()
  })

  it('hides copy button while loading', () => {
    render(<ResultPanel {...defaultProps} result="partial" loading={true} tokenCount={2} />)
    expect(screen.queryByText('复制')).not.toBeInTheDocument()
  })

  // --- Quick start cards ---

  it('renders quick start cards in empty state', () => {
    const onQuickStart = vi.fn()
    render(<ResultPanel {...defaultProps} onQuickStart={onQuickStart} />)
    expect(screen.getByText('写一篇文章')).toBeInTheDocument()
    expect(screen.getByText('润色文本')).toBeInTheDocument()
    expect(screen.getByText('翻译内容')).toBeInTheDocument()
  })

  it('calls onQuickStart with correct task type', () => {
    const onQuickStart = vi.fn()
    render(<ResultPanel {...defaultProps} onQuickStart={onQuickStart} />)
    fireEvent.click(screen.getByText('写一篇文章'))
    expect(onQuickStart).toHaveBeenCalledWith('generate')
    fireEvent.click(screen.getByText('润色文本'))
    expect(onQuickStart).toHaveBeenCalledWith('polish')
    fireEvent.click(screen.getByText('翻译内容'))
    expect(onQuickStart).toHaveBeenCalledWith('translate')
  })

  it('does not render quick start cards when onQuickStart is not provided', () => {
    render(<ResultPanel {...defaultProps} />)
    expect(screen.queryByText('写一篇文章')).not.toBeInTheDocument()
  })

  // --- Word count progress ---

  it('shows word count progress bar when target is set', () => {
    const { container } = render(
      <ResultPanel {...defaultProps} result="测试内容测试内容" tokenCount={5} wordCountTarget={100} />,
    )
    const progressBar = container.querySelector('.word-count-progress')
    expect(progressBar).toBeInTheDocument()
  })

  it('does not show word count progress when target is 0', () => {
    const { container } = render(
      <ResultPanel {...defaultProps} result="测试" tokenCount={5} wordCountTarget={0} />,
    )
    const progressBar = container.querySelector('.word-count-progress')
    expect(progressBar).not.toBeInTheDocument()
  })

  // --- Overflow menu ---

  it('shows overflow menu button (⋯) when result is ready', () => {
    const { container } = render(
      <ResultPanel {...defaultProps} result="some result" tokenCount={5} />,
    )
    const overflowBtn = container.querySelector('.btn-overflow')
    expect(overflowBtn).toBeInTheDocument()
  })

  it('opens overflow menu on click with edit and export options', () => {
    const { container } = render(
      <ResultPanel {...defaultProps} result="some result" tokenCount={5} />,
    )
    const overflowBtn = container.querySelector('.btn-overflow')!
    fireEvent.click(overflowBtn)
    expect(screen.getByText('编辑结果')).toBeInTheDocument()
    expect(screen.getByText('Word (.docx)')).toBeInTheDocument()
    expect(screen.getByText('纯文本 (.txt)')).toBeInTheDocument()
    expect(screen.getByText('Markdown (.md)')).toBeInTheDocument()
    expect(screen.getByText('PDF (.pdf)')).toBeInTheDocument()
  })

  // --- Regenerate button ---

  it('shows regenerate button when onRegenerate is provided', () => {
    render(
      <ResultPanel {...defaultProps} result="some result" tokenCount={5} onRegenerate={vi.fn()} />,
    )
    expect(screen.getByText('换一个')).toBeInTheDocument()
  })

  // --- Token count animation ---

  it('applies token-count-anim class to token count', () => {
    const { container } = render(
      <ResultPanel {...defaultProps} result="some result" tokenCount={10} />,
    )
    const tokenEl = container.querySelector('.token-count-anim')
    expect(tokenEl).toBeInTheDocument()
    expect(tokenEl?.textContent).toBe('10 tokens')
  })

  // --- Accessibility tests ---

  it('error container has role=alert', () => {
    render(<ResultPanel {...defaultProps} error="出错了" />)
    const alert = screen.getByRole('alert')
    expect(alert).toBeInTheDocument()
  })

  it('result content area has aria-live=polite', () => {
    const { container } = render(<ResultPanel {...defaultProps} result="hello" tokenCount={5} />)
    const liveRegion = container.querySelector('[aria-live="polite"]')
    expect(liveRegion).toBeInTheDocument()
  })
})
