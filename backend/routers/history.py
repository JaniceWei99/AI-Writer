from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from db import get_db
from models.history import HistoryRecord
from services.auth import get_current_user_optional

router = APIRouter(prefix="/api/history", tags=["history"])


# ---------- Pydantic schemas ----------

class HistoryCreate(BaseModel):
    task_type: str
    content: str
    result: str = ""
    style: str = ""
    token_count: int = 0


class HistoryOut(BaseModel):
    id: int
    task_type: str
    content: str
    result: str
    style: str
    token_count: int
    created_at: str  # ISO 格式字符串

    model_config = {"from_attributes": True}


def _row_to_out(row: HistoryRecord) -> HistoryOut:
    return HistoryOut(
        id=row.id,
        task_type=row.task_type,
        content=row.content,
        result=row.result,
        style=row.style,
        token_count=row.token_count,
        created_at=row.created_at.isoformat() + "Z" if row.created_at else "",
    )


# ---------- 列表 / 搜索 ----------

@router.get("", response_model=list[HistoryOut])
async def list_history(
    request: Request,
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user_optional(request)
    stmt = (
        select(HistoryRecord)
        .order_by(HistoryRecord.created_at.desc())
    )

    if user:
        stmt = stmt.where(HistoryRecord.user_id == user["id"])
    else:
        stmt = stmt.where(HistoryRecord.user_id.is_(None))

    if keyword:
        kw = f"%{keyword}%"
        stmt = stmt.where(
            HistoryRecord.content.ilike(kw) | HistoryRecord.result.ilike(kw)
        )

    stmt = stmt.offset(offset).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()
    return [_row_to_out(r) for r in rows]


# ---------- 新增 ----------

@router.post("", response_model=HistoryOut, status_code=201)
async def create_history(body: HistoryCreate, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_optional(request)
    record = HistoryRecord(
        user_id=user["id"] if user else None,
        task_type=body.task_type,
        content=body.content,
        result=body.result,
        style=body.style,
        token_count=body.token_count,
        created_at=datetime.now(timezone.utc),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _row_to_out(record)


# ---------- 删除单条 ----------

@router.delete("/{history_id}", status_code=204)
async def delete_one(history_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_optional(request)
    stmt = delete(HistoryRecord).where(HistoryRecord.id == history_id)
    if user:
        stmt = stmt.where(HistoryRecord.user_id == user["id"])
    else:
        stmt = stmt.where(HistoryRecord.user_id.is_(None))
    await db.execute(stmt)
    await db.commit()


# ---------- 清空全部 ----------

@router.delete("", status_code=204)
async def clear_all(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_optional(request)
    stmt = delete(HistoryRecord)
    if user:
        stmt = stmt.where(HistoryRecord.user_id == user["id"])
    else:
        stmt = stmt.where(HistoryRecord.user_id.is_(None))
    await db.execute(stmt)
    await db.commit()
