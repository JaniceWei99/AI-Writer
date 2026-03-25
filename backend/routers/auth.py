import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, field_validator

from db import get_db
from models.user import User
from services.auth import hash_password, verify_password, create_token, get_current_user_required

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger("app.auth")


class RegisterRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 32:
            raise ValueError("用户名长度需为 2-32 个字符")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError("密码长度不能少于 4 个字符")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: int
    username: str


class UserInfo(BaseModel):
    user_id: int
    username: str


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户。"""
    existing = await db.execute(
        select(User).where(User.username == body.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="用户名已存在")

    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("User registered: %s (id=%d)", user.username, user.id)

    token = create_token(user.id, user.username)
    return AuthResponse(token=token, user_id=user.id, username=user.username)


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录。"""
    result = await db.execute(
        select(User).where(User.username == body.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    logger.info("User logged in: %s (id=%d)", user.username, user.id)
    token = create_token(user.id, user.username)
    return AuthResponse(token=token, user_id=user.id, username=user.username)


@router.get("/me", response_model=UserInfo)
async def get_me(user: dict = Depends(get_current_user_required)):
    """获取当前登录用户信息。"""
    return UserInfo(user_id=user["id"], username=user["username"])
