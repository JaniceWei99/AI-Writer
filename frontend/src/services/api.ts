import axios from 'axios'
import type { WritingRequest, WritingResponse } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120_000,
})

export async function processWriting(req: WritingRequest): Promise<WritingResponse> {
  const { data } = await api.post<WritingResponse>('/api/writing/process', req)
  return data
}

export async function streamWriting(
  req: WritingRequest,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): Promise<AbortController> {
  const controller = new AbortController()

  fetch(`${API_BASE}/api/writing/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const reader = res.body?.getReader()
      if (!reader) throw new Error('No reader')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed.startsWith('data: ')) continue
          const payload = trimmed.slice(6)
          if (payload === '[DONE]') {
            onDone()
            return
          }
          try {
            onToken(JSON.parse(payload))
          } catch {
            onToken(payload)
          }
        }
      }
      onDone()
    })
    .catch((err: unknown) => {
      if (err instanceof DOMException && err.name === 'AbortError') return
      onError(err instanceof Error ? err : new Error(String(err)))
    })

  return controller
}

export interface RefineRequest {
  previous_result: string
  feedback: string
  model?: string
  temperature?: number | null
}

export async function streamRefine(
  req: RefineRequest,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): Promise<AbortController> {
  const controller = new AbortController()

  fetch(`${API_BASE}/api/writing/refine`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const reader = res.body?.getReader()
      if (!reader) throw new Error('No reader')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed.startsWith('data: ')) continue
          const payload = trimmed.slice(6)
          if (payload === '[DONE]') {
            onDone()
            return
          }
          try {
            onToken(JSON.parse(payload))
          } catch {
            onToken(payload)
          }
        }
      }
      onDone()
    })
    .catch((err: unknown) => {
      if (err instanceof DOMException && err.name === 'AbortError') return
      onError(err instanceof Error ? err : new Error(String(err)))
    })

  return controller
}

export async function healthCheck(): Promise<boolean> {
  try {
    const { data } = await api.get('/api/health')
    return data.status === 'ok'
  } catch {
    return false
  }
}

export interface ModelsResult {
  models: string[]
  default: string
}

export async function fetchModels(): Promise<ModelsResult> {
  try {
    const { data } = await api.get<ModelsResult>('/api/models')
    return data
  } catch {
    return { models: [], default: '' }
  }
}

export interface UploadResult {
  filename: string
  text: string
  char_count: number
}

export async function uploadFile(file: File): Promise<UploadResult> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<UploadResult>('/api/writing/upload', formData)
  return data
}

export async function downloadDocx(content: string, title: string = ''): Promise<void> {
  const defaultName = (title || '导出文档') + '.docx'

  // 先弹窗拿文件句柄（必须在用户手势的同步上下文中调用）
  let fileHandle: any = null
  if ('showSaveFilePicker' in window) {
    try {
      fileHandle = await (window as any).showSaveFilePicker({
        suggestedName: defaultName,
        types: [{
          description: 'Word 文档',
          accept: { 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
        }],
      })
    } catch (e: any) {
      if (e?.name === 'AbortError') return // 用户取消
    }
  }

  const { data } = await api.post('/api/writing/export-docx', { content, title }, {
    responseType: 'blob',
  })

  if (fileHandle) {
    const writable = await fileHandle.createWritable()
    await writable.write(data)
    await writable.close()
    return
  }

  // 回退：直接下载到浏览器默认下载目录
  const url = URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = url
  a.download = defaultName
  a.click()
  URL.revokeObjectURL(url)
}

function downloadBlob(content: string, filename: string, mime: string): void {
  const blob = new Blob([content], { type: `${mime};charset=utf-8` })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function downloadTxt(content: string, title: string = ''): void {
  downloadBlob(content, (title || '导出文档') + '.txt', 'text/plain')
}

export function downloadMd(content: string, title: string = ''): void {
  downloadBlob(content, (title || '导出文档') + '.md', 'text/markdown')
}

export async function downloadPdf(content: string, title: string = ''): Promise<void> {
  const defaultName = (title || '导出文档') + '.pdf'
  const { data } = await api.post('/api/writing/export-pdf', { content, title }, {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = url
  a.download = defaultName
  a.click()
  URL.revokeObjectURL(url)
}

export async function downloadPptx(
  content: string,
  title: string = '',
  template: string = 'business',
  withImages: boolean = false,
  unsplashKey: string = '',
): Promise<void> {
  const defaultName = (title || '演示文稿') + '.pptx'
  const { data } = await api.post('/api/writing/export-pptx', {
    content, title, template,
    with_images: withImages,
    unsplash_key: unsplashKey,
  }, {
    responseType: 'blob',
    timeout: withImages ? 300_000 : 120_000,  // longer timeout when fetching images
  })
  const url = URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = url
  a.download = defaultName
  a.click()
  URL.revokeObjectURL(url)
}
