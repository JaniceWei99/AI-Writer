import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, timezone

from db import get_db
from models.custom_style import CustomStyle

router = APIRouter(prefix="/api/styles", tags=["styles"])

# Built-in style slugs that cannot be overridden
BUILTIN_SLUGS = frozenset({
    "", "literary", "sh_gaokao", "xiaohongshu", "gongzhonghao",
    "toutiao", "zhihu", "ai_drama", "ppt",
})

SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,62}$")


# ---------- Pydantic schemas ----------

class StyleCreate(BaseModel):
    name: str
    slug: str
    prompt_template: str
    description: str = ""

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        v = v.strip().lower()
        if v in BUILTIN_SLUGS:
            raise ValueError(f"'{v}' 是内置风格，不可使用")
        if not SLUG_PATTERN.match(v):
            raise ValueError("slug 必须以小写字母开头，只含小写字母、数字、下划线，2-63 字符")
        return v

    @field_validator("prompt_template")
    @classmethod
    def validate_template(cls, v: str) -> str:
        if "{content}" not in v:
            raise ValueError("prompt_template 必须包含 {content} 占位符")
        return v


class StyleUpdate(BaseModel):
    name: Optional[str] = None
    prompt_template: Optional[str] = None
    description: Optional[str] = None

    @field_validator("prompt_template")
    @classmethod
    def validate_template(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and "{content}" not in v:
            raise ValueError("prompt_template 必须包含 {content} 占位符")
        return v


class StyleOut(BaseModel):
    id: int
    name: str
    slug: str
    prompt_template: str
    description: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


def _row_to_out(row: CustomStyle) -> StyleOut:
    return StyleOut(
        id=row.id,
        name=row.name,
        slug=row.slug,
        prompt_template=row.prompt_template,
        description=row.description,
        created_at=row.created_at.isoformat() + "Z" if row.created_at else "",
        updated_at=row.updated_at.isoformat() + "Z" if row.updated_at else "",
    )


# ---------- 列表 ----------

@router.get("", response_model=list[StyleOut])
async def list_styles(db: AsyncSession = Depends(get_db)):
    stmt = select(CustomStyle).order_by(CustomStyle.created_at.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return [_row_to_out(r) for r in rows]


# ---------- 新增 ----------

@router.post("", response_model=StyleOut, status_code=201)
async def create_style(body: StyleCreate, db: AsyncSession = Depends(get_db)):
    # Check uniqueness
    existing = await db.execute(
        select(CustomStyle).where(CustomStyle.slug == body.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"slug '{body.slug}' 已存在")

    record = CustomStyle(
        name=body.name,
        slug=body.slug,
        prompt_template=body.prompt_template,
        description=body.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _row_to_out(record)


# ---------- 更新 ----------

@router.put("/{style_id}", response_model=StyleOut)
async def update_style(style_id: int, body: StyleUpdate, db: AsyncSession = Depends(get_db)):
    record = await db.get(CustomStyle, style_id)
    if not record:
        raise HTTPException(status_code=404, detail="风格模板不存在")

    if body.name is not None:
        record.name = body.name
    if body.prompt_template is not None:
        record.prompt_template = body.prompt_template
    if body.description is not None:
        record.description = body.description
    record.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)
    return _row_to_out(record)


# ---------- 删除 ----------

@router.delete("/{style_id}", status_code=204)
async def delete_style(style_id: int, db: AsyncSession = Depends(get_db)):
    stmt = delete(CustomStyle).where(CustomStyle.id == style_id)
    await db.execute(stmt)
    await db.commit()
