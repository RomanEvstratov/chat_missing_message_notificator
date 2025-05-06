from datetime import timedelta, datetime, UTC
from typing import Sequence

from telethon import TelegramClient
from telethon.tl.custom import Message

from src.settings import log


class TGClient:
    def __init__(self, phone_number: str, api_id: int, api_hash: str):
        self.phone_number = phone_number
        self.client = TelegramClient("tg_session", api_id, api_hash)

    def is_passed_message(self, message: Message, approved_users: Sequence[int]) -> bool:
        if datetime.now(UTC) > message.date + timedelta(seconds=15):
            if message.sender_id in approved_users:
                return True
            elif message.reactions and message.reactions.recent_reactions:
                for reaction in message.reactions.recent_reactions:
                    if str(reaction.peer_id.user_id) in approved_users:
                        return True
        return False


    async def check_chat_messages(self, blacklist: Sequence[str], approved_users: Sequence[int]) -> list[str]:
        log.info("Проверка чатов")
        try:
            await self.client.start(self.phone_number)
            if not self.client.is_connected():
                log.info("Подключение телеграм клиента")
                await self.client.connect()
            chats = []
            async for dialog in self.client.iter_dialogs():
                if dialog.name in blacklist:
                    continue
                async for message in self.client.iter_messages(dialog, limit=1):
                    if not message:
                        continue
                    elif not self.is_passed_message(message, approved_users):
                        chats.append(dialog.name)
            return chats
        except Exception as exc:
            log.info(f"{exc}")