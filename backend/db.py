from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import os
import logging

logger = logging.getLogger("app.db")

# Default: SQLite at backend/data/app.db (local mode)
# Override with DATABASE_URL env var for shared deployment (e.g. PostgreSQL)
_DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")
os.makedirs(os.path.dirname(_DEFAULT_DB_PATH), exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{_DEFAULT_DB_PATH}")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Lightweight migration: add user_id column to history if missing
        try:
            await conn.execute(text(
                "ALTER TABLE history ADD COLUMN user_id INTEGER REFERENCES users(id)"
            ))
            logger.info("Migration: added user_id column to history table")
        except Exception:
            pass  # Column already exists


async def get_db() -> AsyncSession:  # type: ignore[misc]
    async with async_session() as session:
        yield session
