import asyncio
import logging
from typing import Any

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from src.settings import log


class SlackClient:
    def __init__(self, token: str, channel: str):
        self.slack_client = AsyncWebClient(token=token)
        self.slack_channel = channel

    async def send_slack_notification_about_chat(self, chat: str):
        """Отправка уведомления в Slack."""
        try:
            await self.slack_client.chat_postMessage(
                channel=self.slack_channel,
                text=f"Менеджер не ответил на сообщение в чате {chat}",
            )
            log.info(f"Slack уведомление о чате отправлено: {chat}")
        except SlackApiError as e:
            log.info(f"Ошибка при отправке сообщения в Slack: {e.response['error']}")

    async def notify_about_chat(self, chats: list[str]):
        """Отправка уведомления в Slack."""
        try:
            log.info(f"На отправку {len(chats)}")
            await asyncio.gather(
                *(self.send_slack_notification_about_chat(chat) for chat in chats),
                return_exceptions=True
            )
            log.info(f"Slack уведомления отправлены")
        except SlackApiError as e:
            log.info(f"Ошибка при отправке сообщения в Slack: {e.response['error']}")
