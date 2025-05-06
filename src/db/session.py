from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.settings import settings

sync_engine = create_engine(
    settings.DATABASE.sync_db_url.get_secret_value(),
    echo=True,
    pool_pre_ping=True,
)
async_engine = create_async_engine(
    settings.DATABASE.async_db_url.get_secret_value(),
    echo=True,
)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)
