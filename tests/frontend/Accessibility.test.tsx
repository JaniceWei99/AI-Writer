import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import ConfirmDialog from '@/components/ConfirmDialog'
import SettingsPanel, { type AppSettings } from '@/components/SettingsPanel'
import AuthPanel from '@/components/AuthPanel'
import StyleEditor from '@/components/StyleEditor'

// --- ConfirmDialog ---

describe('ConfirmDialog accessibility', () => {
  const defaultProps = {
    message: '确认删除？',
    onConfirm: vi.fn(),
    onCancel: vi.fn(),
  }

  it('has role=alertdialog', () => {
    render(<ConfirmDialog {...defaultProps} />)
    expect(screen.getByRole('alertdialog')).toBeInTheDocument()
  })

  it('has aria-modal=true', () => {
    render(<ConfirmDialog {...defaultProps} />)
    expect(screen.getByRole('alertdialog')).toHaveAttribute('aria-modal', 'true')
  })

  it('overlay has role=presentation', () => {
    render(<ConfirmDialog {...defaultProps} />)
    expect(screen.getByRole('presentation')).toBeInTheDocument()
  })

  it('has aria-describedby linking to message', () => {
    render(<ConfirmDialog {...defaultProps} />)
    const dialog = screen.getByRole('alertdialog')
    const describedById = dialog.getAttribute('aria-describedby')
    expect(describedById).toBeTruthy()
    const target = document.getElementById(describedById!)
    expect(target).toBeInTheDocument()
    expect(target?.textContent).toBe('确认删除？')
  })
})

// --- SettingsPanel ---

describe('SettingsPanel accessibility', () => {
  const defaultSettings: AppSettings = {
    model: 'qwen3.5:9b',
    temperature: 0.7,
    unsplashKey: '',
  }

  const defaultProps = {
    settings: defaultSettings,
    onSave: vi.fn(),
    onClose: vi.fn(),
  }

  it('has role=dialog', () => {
    render(<SettingsPanel {...defaultProps} />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('has aria-modal=true', () => {
    render(<SettingsPanel {...defaultProps} />)
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true')
  })

  it('has aria-labelledby linking to title', () => {
    render(<SettingsPanel {...defaultProps} />)
    const dialog = screen.getByRole('dialog')
    const labelledById = dialog.getAttribute('aria-labelledby')
    expect(labelledById).toBeTruthy()
    const target = document.getElementById(labelledById!)
    expect(target).toBeInTheDocument()
  })

  it('close button has aria-label', () => {
    render(<SettingsPanel {...defaultProps} />)
    expect(screen.getByLabelText('关闭设置')).toBeInTheDocument()
  })
})

// --- AuthPanel ---

describe('AuthPanel accessibility', () => {
  const defaultProps = {
    user: null,
    onAuthChange: vi.fn(),
  }

  it('modal has role=dialog when open', async () => {
    render(<AuthPanel {...defaultProps} />)
    await act(async () => {
      fireEvent.click(screen.getByText('登录'))
    })
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('modal has aria-modal=true', async () => {
    render(<AuthPanel {...defaultProps} />)
    await act(async () => {
      fireEvent.click(screen.getByText('登录'))
    })
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true')
  })

  it('modal has aria-labelledby linking to title', async () => {
    render(<AuthPanel {...defaultProps} />)
    await act(async () => {
      fireEvent.click(screen.getByText('登录'))
    })
    const dialog = screen.getByRole('dialog')
    const labelledById = dialog.getAttribute('aria-labelledby')
    expect(labelledById).toBeTruthy()
    const target = document.getElementById(labelledById!)
    expect(target).toBeInTheDocument()
  })

  it('close button has aria-label', async () => {
    render(<AuthPanel {...defaultProps} />)
    await act(async () => {
      fireEvent.click(screen.getByText('登录'))
    })
    expect(screen.getByLabelText('关闭')).toBeInTheDocument()
  })
})

// --- StyleEditor ---

describe('StyleEditor accessibility', () => {
  const defaultProps = {
    onClose: vi.fn(),
    onStylesChange: vi.fn(),
  }

  it('has role=dialog', () => {
    render(<StyleEditor {...defaultProps} />)
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })

  it('has aria-modal=true', () => {
    render(<StyleEditor {...defaultProps} />)
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true')
  })

  it('has aria-labelledby linking to title', () => {
    render(<StyleEditor {...defaultProps} />)
    const dialog = screen.getByRole('dialog')
    const labelledById = dialog.getAttribute('aria-labelledby')
    expect(labelledById).toBeTruthy()
    const target = document.getElementById(labelledById!)
    expect(target).toBeInTheDocument()
  })

  it('close button has aria-label', () => {
    render(<StyleEditor {...defaultProps} />)
    expect(screen.getByLabelText('关闭')).toBeInTheDocument()
  })
})
