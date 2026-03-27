import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('axios', () => {
  const instance = {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  }
  return {
    default: {
      create: vi.fn(() => instance),
      ...instance,
    },
    __mockInstance: instance,
  }
})

vi.mock('@/services/auth', () => ({
  getToken: vi.fn(() => null),
}))

// Import after mocking
const { getHistory, addHistory, removeHistory, clearHistory } = await import('@/services/history')
const mockAxios = (axios as any).create()

describe('history service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns empty array when API returns empty', async () => {
    mockAxios.get.mockResolvedValueOnce({ data: [] })
    const result = await getHistory()
    expect(result).toEqual([])
    expect(mockAxios.get).toHaveBeenCalledWith('/api/history')
  })

  it('addHistory creates an entry and returns it', async () => {
    const mockResponse = {
      id: 1,
      task_type: 'generate',
      content: '测试',
      result: '结果',
      style: '',
      token_count: 5,
      created_at: '2026-03-26T10:00:00Z',
    }
    mockAxios.post.mockResolvedValueOnce({ data: mockResponse })

    const entry = await addHistory({
      task_type: 'generate',
      content: '测试',
      result: '结果',
      style: '',
      token_count: 5,
    })
    expect(entry.id).toBe('1')
    expect(entry.content).toBe('测试')
    expect(mockAxios.post).toHaveBeenCalledWith('/api/history', expect.objectContaining({ content: '测试' }))
  })

  it('getHistory converts numeric ids to strings', async () => {
    const mockData = [
      { id: 2, task_type: 'polish', content: 'second', result: 'r2', style: '', token_count: 2, created_at: '2026-03-26T11:00:00Z' },
      { id: 1, task_type: 'generate', content: 'first', result: 'r1', style: '', token_count: 1, created_at: '2026-03-26T10:00:00Z' },
    ]
    mockAxios.get.mockResolvedValueOnce({ data: mockData })

    const list = await getHistory()
    expect(list).toHaveLength(2)
    expect(list[0].id).toBe('2')
    expect(list[1].id).toBe('1')
    expect(list[0].content).toBe('second')
  })

  it('removeHistory calls DELETE with correct id', async () => {
    mockAxios.delete.mockResolvedValueOnce({ data: null })
    await removeHistory('42')
    expect(mockAxios.delete).toHaveBeenCalledWith('/api/history/42')
  })

  it('clearHistory calls DELETE on base endpoint', async () => {
    mockAxios.delete.mockResolvedValueOnce({ data: null })
    await clearHistory()
    expect(mockAxios.delete).toHaveBeenCalledWith('/api/history')
  })

  it('handles API errors gracefully', async () => {
    mockAxios.get.mockRejectedValueOnce(new Error('Network Error'))
    await expect(getHistory()).rejects.toThrow('Network Error')
  })
})
