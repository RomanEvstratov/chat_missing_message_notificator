from datetime import timedelta, datetime, UTC
from typing import Sequence

from telethon import TelegramClient
from telethon.tl.custom import Message

from src.exceptions import DefaultException
from src.settings import log


class TGClient:
    def __init__(self, phone_number: str, api_id: int, api_hash: str):
        self.phone_number = phone_number
        self.client = TelegramClient("tg_session", api_id, api_hash)
        self.in_session = False

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
        except DefaultException as exc:
            raise exc
        except Exception as exc:
            log.info(f"{exc}")

    async def start(self):
        try:
            if not self.client.is_connected():
                log.info("Подключение телеграм клиента")
                await self.client.connect()
                is_auth = await self.client.is_user_authorized()
                if not is_auth:
                    # await self.client.send_code_request(self.phone_number)
                    raise DefaultException("Not authorized")
            await self.client.start(self.phone_number)
            self.in_session = True
        except DefaultException as exc:
            log.info(f"{exc}")
            if self.in_session:
                self.in_session = False
                await self.client.log_out()
            raise exc
