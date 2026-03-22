export const TaskType = {
  GENERATE: 'generate',
  POLISH: 'polish',
  TRANSLATE: 'translate',
  SUMMARIZE: 'summarize',
} as const

export type TaskType = (typeof TaskType)[keyof typeof TaskType]

export interface WritingRequest {
  task_type: TaskType
  content: string
  style: string
  target_lang: string
  attachment_text: string
  model?: string
  temperature?: number
}

export interface WritingResponse {
  task_type: TaskType
  result: string
  token_count: number
}

export const TASK_LABELS: Record<TaskType, string> = {
  [TaskType.GENERATE]: '文章生成',
  [TaskType.POLISH]: '文本润色',
  [TaskType.TRANSLATE]: '文本翻译',
  [TaskType.SUMMARIZE]: '文本摘要',
}

export const TASK_PLACEHOLDERS: Record<TaskType, string> = {
  [TaskType.GENERATE]: '请输入主题或大纲，例如：写一篇关于人工智能未来发展的文章...',
  [TaskType.POLISH]: '请粘贴需要润色的文本...',
  [TaskType.TRANSLATE]: '请输入需要翻译的文本...',
  [TaskType.SUMMARIZE]: '请粘贴需要总结的长文本...',
}

export const STYLE_OPTIONS = [
  { value: '', label: '默认' },
  { value: 'literary', label: '文学' },
  { value: 'sh_gaokao', label: '上海高考作文' },
  { value: 'xiaohongshu', label: '小红书爆款' },
  { value: 'gongzhonghao', label: '公众号文案' },
  { value: 'toutiao', label: '头条文案' },
  { value: 'ai_drama', label: 'AI短剧脚本' },
]

export const LANG_OPTIONS = [
  { value: '英文', label: '英文' },
  { value: '中文', label: '中文' },
  { value: '日文', label: '日文' },
  { value: '韩文', label: '韩文' },
  { value: '法文', label: '法文' },
  { value: '德文', label: '德文' },
]

export interface HistoryItem {
  id: string
  task_type: TaskType
  content: string
  result: string
  style: string
  token_count: number
  created_at: string
}
