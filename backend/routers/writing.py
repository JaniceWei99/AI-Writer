import io
import json
import logging
from urllib.parse import quote

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from models.schemas import WritingRequest, WritingResponse, ExportRequest, ExportPptxRequest, RefineRequest, OutlineRequest, ExpandChapterRequest
from models.custom_style import CustomStyle
from prompts.writing import build_prompt, build_refine_prompt, build_outline_prompt, build_expand_chapter_prompt, is_poetry_request, validate_poetry
from services.llm_provider import generate, generate_stream, get_default_model
from services.file_parser import extract_text
from services.docx_export import markdown_to_docx
from services.pdf_export import markdown_to_pdf
from services.pptx_export import markdown_to_pptx, _parse_slides
from db import async_session

router = APIRouter(prefix="/api/writing", tags=["writing"])
logger = logging.getLogger("app.writing")

MAX_POETRY_RETRIES = 3


async def _get_custom_prompt(style: str) -> str:
    """Look up a custom style template from DB. Returns empty string if not found."""
    if not style:
        return ""
    async with async_session() as session:
        row = await session.execute(
            select(CustomStyle.prompt_template).where(CustomStyle.slug == style)
        )
        result = row.scalar_one_or_none()
        return result or ""


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件并提取文本内容。支持 PDF、Word、PPT、TXT 等格式。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")
    try:
        file_bytes = await file.read()
        text = extract_text(file.filename, file_bytes)
        logger.info("File uploaded: %s (%d bytes -> %d chars)", file.filename, len(file_bytes), len(text))
        return {"filename": file.filename, "text": text, "char_count": len(text)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")


@router.post("/process", response_model=WritingResponse)
async def process_writing(req: WritingRequest):
    """非流式处理写作请求，返回完整结果。"""
    default_model = get_default_model()
    logger.info("Process request: task=%s model=%s content_len=%d", req.task_type.value, req.model or default_model, len(req.content))
    custom_tpl = await _get_custom_prompt(req.style)
    prompt = build_prompt(
        task_type=req.task_type.value,
        content=req.content,
        style=req.style,
        target_lang=req.target_lang,
        attachment_text=req.attachment_text,
        custom_prompt_template=custom_tpl,
    )
    model = req.model or default_model
    temp = req.temperature

    is_poetry = req.task_type.value == "generate" and is_poetry_request(req.content)

    for attempt in range(MAX_POETRY_RETRIES if is_poetry else 1):
        result = await generate(prompt, model=model, temperature=temp)
        text = result["text"]
        if not is_poetry or validate_poetry(text, req.content):
            break

    return WritingResponse(
        task_type=req.task_type,
        result=result["text"],
        token_count=result["token_count"],
    )


@router.post("/stream")
async def stream_writing(req: WritingRequest):
    """流式处理写作请求，实时返回文本。"""
    default_model = get_default_model()
    logger.info("Stream request: task=%s style=%s model=%s content_len=%d", req.task_type.value, req.style, req.model or default_model, len(req.content))
    custom_tpl = await _get_custom_prompt(req.style)
    is_poetry = req.task_type.value == "generate" and is_poetry_request(req.content) and not custom_tpl
    model = req.model or default_model
    temp = req.temperature

    if is_poetry:
        prompt = build_prompt(
            task_type=req.task_type.value,
            content=req.content,
            style=req.style,
            target_lang=req.target_lang,
            attachment_text=req.attachment_text,
        )
        for attempt in range(MAX_POETRY_RETRIES):
            result = await generate(prompt, model=model, temperature=temp)
            text = result["text"]
            if validate_poetry(text, req.content):
                break

        async def poetry_generator():
            for char in text:
                yield f"data: {json.dumps(char)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(poetry_generator(), media_type="text/event-stream")

    prompt = build_prompt(
        task_type=req.task_type.value,
        content=req.content,
        style=req.style,
        target_lang=req.target_lang,
        attachment_text=req.attachment_text,
        custom_prompt_template=custom_tpl,
    )

    async def event_generator():
        async for token in generate_stream(prompt, model=model, temperature=temp):
            yield f"data: {json.dumps(token)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/refine")
async def refine_writing(req: RefineRequest):
    """流式处理继续对话/修改请求，根据用户反馈优化之前的结果。"""
    logger.info("Refine request: feedback_len=%d prev_len=%d", len(req.feedback), len(req.previous_result))
    model = req.model or get_default_model()
    temp = req.temperature
    prompt = build_refine_prompt(req.previous_result, req.feedback)

    async def event_generator():
        async for token in generate_stream(prompt, model=model, temperature=temp):
            yield f"data: {json.dumps(token)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/outline")
async def generate_outline(req: OutlineRequest):
    """流式生成文章大纲，用于长文分章节写作。"""
    logger.info("Outline request: content_len=%d style=%s", len(req.content), req.style)
    model = req.model or get_default_model()
    temp = req.temperature
    prompt = build_outline_prompt(req.content, req.style)

    async def event_generator():
        async for token in generate_stream(prompt, model=model, temperature=temp):
            yield f"data: {json.dumps(token)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/expand-chapter")
async def expand_chapter(req: ExpandChapterRequest):
    """流式展开单个章节内容。"""
    logger.info("Expand chapter: title=%s outline_len=%d", req.chapter_title, len(req.outline))
    model = req.model or get_default_model()
    temp = req.temperature
    prompt = build_expand_chapter_prompt(req.outline, req.chapter_title, req.chapter_desc, req.style)

    async def event_generator():
        async for token in generate_stream(prompt, model=model, temperature=temp):
            yield f"data: {json.dumps(token)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/export-docx")
async def export_docx(req: ExportRequest):
    """将 Markdown 文本导出为 Word 文档。"""
    try:
        buf = markdown_to_docx(req.content, req.title)
        filename = (req.title or "导出文档") + ".docx"
        encoded = quote(filename)
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档生成失败: {str(e)}")


@router.post("/export-pdf")
async def export_pdf(req: ExportRequest):
    """将 Markdown 文本导出为 PDF 文档。"""
    try:
        buf = markdown_to_pdf(req.content, req.title)
        filename = (req.title or "导出文档") + ".pdf"
        encoded = quote(filename)
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 生成失败: {str(e)}")


@router.post("/export-pptx")
async def export_pptx(req: ExportPptxRequest):
    """将 Markdown PPT 大纲导出为 PowerPoint 文件。"""
    try:
        images: dict[int, bytes] = {}

        if req.with_images:
            from services.unsplash import fetch_images_for_slides
            slides_data = _parse_slides(req.content)
            # Only fetch images for content slides (skip cover=0 and end)
            titles = [sd.title for sd in slides_data]
            # Skip first slide (cover) and last slide (thanks/Q&A)
            content_indices = list(range(1, max(len(titles) - 1, 1)))
            content_titles = [titles[j] for j in content_indices if j < len(titles)]
            if content_titles:
                raw_images = await fetch_images_for_slides(
                    content_titles,
                    access_key=req.unsplash_key,
                )
                # Map back to original slide indices
                for local_idx, img_bytes in raw_images.items():
                    images[content_indices[local_idx]] = img_bytes

        buf = markdown_to_pptx(req.content, req.title, template=req.template, images=images)
        filename = (req.title or "演示文稿") + ".pptx"
        encoded = quote(filename)
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPT 生成失败: {str(e)}")
