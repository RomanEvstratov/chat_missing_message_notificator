from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import BlackListChat, OurUser


class NotificatorRepository:
    @staticmethod
    async def get_blacklisted_chats(session: AsyncSession) -> Sequence[str]:
        statement = select(BlackListChat.name)
        result = await session.scalars(statement)
        return result.all()

    @staticmethod
    async def get_our_users(session: AsyncSession) -> Sequence[str]:
        statement = select(OurUser.username)
        result = await session.scalars(statement)
        return result.all()