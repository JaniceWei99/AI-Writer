import { describe, it, expect, beforeEach } from 'vitest'
import { getHistory, addHistory, removeHistory, clearHistory } from '@/services/history'

describe('history service', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns empty array when no history', () => {
    expect(getHistory()).toEqual([])
  })

  it('addHistory creates an entry with id and created_at', () => {
    const entry = addHistory({
      task_type: 'generate',
      content: '测试',
      result: '结果',
      style: '',
      token_count: 5,
    })
    expect(entry.id).toBeTruthy()
    expect(entry.created_at).toBeTruthy()
    expect(entry.content).toBe('测试')
  })

  it('getHistory returns items in newest-first order', () => {
    addHistory({ task_type: 'generate', content: 'first', result: 'r1', style: '', token_count: 1 })
    addHistory({ task_type: 'polish', content: 'second', result: 'r2', style: '', token_count: 2 })
    const list = getHistory()
    expect(list).toHaveLength(2)
    expect(list[0].content).toBe('second')
    expect(list[1].content).toBe('first')
  })

  it('removeHistory deletes the given item', () => {
    const a = addHistory({ task_type: 'generate', content: 'a', result: 'ra', style: '', token_count: 1 })
    addHistory({ task_type: 'generate', content: 'b', result: 'rb', style: '', token_count: 1 })
    removeHistory(a.id)
    const list = getHistory()
    expect(list).toHaveLength(1)
    expect(list[0].content).toBe('b')
  })

  it('clearHistory removes all items', () => {
    addHistory({ task_type: 'generate', content: 'x', result: 'rx', style: '', token_count: 1 })
    addHistory({ task_type: 'generate', content: 'y', result: 'ry', style: '', token_count: 1 })
    clearHistory()
    expect(getHistory()).toEqual([])
  })

  it('limits to 50 items', () => {
    for (let i = 0; i < 55; i++) {
      addHistory({ task_type: 'generate', content: `item${i}`, result: `r${i}`, style: '', token_count: 1 })
    }
    expect(getHistory()).toHaveLength(50)
  })

  it('handles corrupted localStorage gracefully', () => {
    localStorage.setItem('writing_history', 'not valid json')
    expect(getHistory()).toEqual([])
  })
})
