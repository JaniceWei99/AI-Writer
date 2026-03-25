"""Simple JWT authentication service."""

import os
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db import get_db
from models.user import User

JWT_SECRET = os.getenv("JWT_SECRET", "ai-writing-assistant-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "72"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: int, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的认证令牌")


def _extract_token(request: Request) -> Optional[str]:
    """Extract JWT token from Authorization header. Returns None if not present."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


async def get_current_user_optional(request: Request) -> Optional[dict]:
    """Extract user from token if present. Returns None for anonymous users."""
    token = _extract_token(request)
    if not token:
        return None
    try:
        payload = decode_token(token)
        return {"id": payload["sub"], "username": payload["username"]}
    except HTTPException:
        return None


async def get_current_user_required(request: Request) -> dict:
    """Require a valid JWT token. Raises 401 if not authenticated."""
    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    payload = decode_token(token)
    return {"id": payload["sub"], "username": payload["username"]}
