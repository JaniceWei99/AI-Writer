import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ResultPanel from '@/components/ResultPanel'

describe('ResultPanel', () => {
  it('shows empty hint when no result and not loading', () => {
    render(<ResultPanel result="" loading={false} tokenCount={0} error="" />)
    expect(screen.getByText(/开始处理/)).toBeInTheDocument()
  })

  it('shows error message', () => {
    render(<ResultPanel result="" loading={false} tokenCount={0} error="连接失败" />)
    expect(screen.getByText('出错了')).toBeInTheDocument()
    expect(screen.getByText('连接失败')).toBeInTheDocument()
  })

  it('renders markdown result', () => {
    render(<ResultPanel result="**bold text**" loading={false} tokenCount={10} error="" />)
    expect(screen.getByText('bold text')).toBeInTheDocument()
    expect(screen.getByText('10 tokens')).toBeInTheDocument()
  })

  it('shows generating indicator while loading', () => {
    render(<ResultPanel result="partial" loading={true} tokenCount={3} error="" />)
    expect(screen.getByText('生成中...')).toBeInTheDocument()
  })

  it('shows copy button when result is ready', () => {
    render(<ResultPanel result="some result" loading={false} tokenCount={5} error="" />)
    expect(screen.getByText('复制结果')).toBeInTheDocument()
  })

  it('hides copy button while loading', () => {
    render(<ResultPanel result="partial" loading={true} tokenCount={2} error="" />)
    expect(screen.queryByText('复制结果')).not.toBeInTheDocument()
  })
})
