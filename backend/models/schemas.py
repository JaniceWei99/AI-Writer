from typing import Optional
from pydantic import BaseModel
from enum import Enum


class TaskType(str, Enum):
    GENERATE = "generate"
    POLISH = "polish"
    TRANSLATE = "translate"
    SUMMARIZE = "summarize"


class WritingRequest(BaseModel):
    task_type: TaskType
    content: str
    # 文章生成时用作主题/大纲，其他任务用作输入文本
    style: str = ""
    # 润色风格：formal / casual / academic 等
    target_lang: str = "英文"
    # 翻译目标语言
    attachment_text: str = ""
    # 上传附件提取的文本内容，作为参考资料
    model: str = ""
    # 自定义模型名称，为空则使用服务端默认值
    temperature: Optional[float] = None
    # 生成温度，None 则使用模型默认值


class WritingResponse(BaseModel):
    task_type: TaskType
    result: str
    token_count: int = 0


class ExportRequest(BaseModel):
    content: str
    title: str = ""


class RefineRequest(BaseModel):
    previous_result: str
    # 上一次 AI 生成的完整结果
    feedback: str
    # 用户对结果的修改意见
    model: str = ""
    temperature: Optional[float] = None


class ExportPptxRequest(BaseModel):
    content: str
    title: str = ""
    template: str = "business"
    with_images: bool = False
    unsplash_key: str = ""
