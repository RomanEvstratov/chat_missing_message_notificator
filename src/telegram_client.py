import os.path
from datetime import timedelta, datetime
from typing import Sequence

from pyrogram import Client, types
from pyrogram.errors import PhoneCodeInvalid, AuthKeyUnregistered, BroadcastForbidden
from pyrogram.raw.functions.messages import GetMessageReactionsList

from src.exceptions import DefaultException
from src.settings import log, SESSION_FILE_PATH


class TGClient:
    def __init__(self, phone_number: str, api_id: int, api_hash: str):
        self.phone_number = phone_number
        self.client = Client("tg_session", api_id, api_hash)

    async def is_passed_message(self, message: types.Message, approved_users: Sequence[str]) -> bool:
        try:
            if datetime.now() > message.date + timedelta(minutes=15):
                if message.from_user and message.from_user.username in approved_users:
                    return True
                elif message.reactions:
                    peer = await self.client.resolve_peer(message.chat.id)
                    reactions = await self.client.invoke(GetMessageReactionsList(peer=peer, id=message.id, limit=-1))
                    for user in reactions.users:
                        if user.username and user.username in approved_users:
                            return True
            return False
        except BroadcastForbidden as exc:
            log.error(f"{exc}")
            if message.reactions and message.reactions.reactions:
                for reaction in message.reactions.reactions:
                    if reaction.chosen_order is not None:
                        return True
                return False
            return True

    async def check_chat_messages(self, blacklist: Sequence[str], approved_users: Sequence[str]) -> list[str]:
        log.info("Проверка чатов")
        try:
            chats = []
            async for dialog in self.client.get_dialogs():
                if (
                    dialog.chat.first_name in blacklist
                    or dialog.chat.last_name in blacklist
                    or dialog.chat.username in blacklist
                    or dialog.chat.title in blacklist
                ):
                    continue
                if dialog.top_message:
                    is_passed = await self.is_passed_message(dialog.top_message, approved_users)
                    if not is_passed:
                        title = (
                            dialog.chat.first_name
                            or dialog.chat.last_name
                            or dialog.chat.username
                            or dialog.chat.title
                        )
                        if title:
                            chats.append(title)
            return chats
        except AuthKeyUnregistered as exc:
            log.info(f"Текущая сессия недействительна. Необходимо войти повторно.")
            await self.disconnect()
            await self.client.storage.delete()
            raise DefaultException()

        except Exception as exc:
            log.info(f"{exc}")

    async def connect(self):
        log.info("Происходит попытка соединения с сессией")
        return await self.client.connect()

    async def send_code(self) -> str:
        try:
            log.info("Запрос на отправку кода доступа")
            send_code_info = await self.client.send_code(self.phone_number)
            return send_code_info.phone_code_hash
        except Exception as exc:
            return

    async def sign_in(self, phone_code_hash: str) -> None:
        log.info("Ожидание ввода кода верификации")
        phone_code = input("Введите код верификации: ")
        try:
            return await self.client.sign_in(self.phone_number, phone_code_hash, phone_code)
        except PhoneCodeInvalid as exc:
            log.info("Код верификации не валидный")
            await self.sign_in(phone_code_hash)

    async def get_me(self) -> types.User:
        return await self.client.get_me()

    async def disconnect(self) -> None:
        if self.client.is_connected:
            log.info("Разьединение от сессии")
            await self.client.disconnect()

    async def login(self):
        if os.path.exists(SESSION_FILE_PATH):
            log.info("Сессия уже существует")
            return True
        log.info("Отсутствует сессия")
        await self.client.connect()
        phone_code_hash = await self.send_code()
        return await self.sign_in(phone_code_hash)
