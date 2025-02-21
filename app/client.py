import asyncio
from telethon import TelegramClient
from slack_sdk import WebClient as SlackClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta

from app.utils import check_time, sleep_until_morning


class ManagerNotifier:
    final_check_time = datetime.strptime("20:00", "%H:%M").time()
    final_check_done = False  # Флаг для предотвращения повторного финального чека

    def __init__(
        self,
        telegram_client: TelegramClient,
        slack_client: SlackClient,
        slack_channel: str,
        chat_list: list[str],
        black_list: list[str],
        our_users_ids: list[str],
    ) -> None:
        self.telegram_client = telegram_client
        self.slack_client = slack_client
        self.slack_channel = slack_channel
        self.chat_list = chat_list
        self.black_list = black_list
        self.our_users_ids = our_users_ids

    async def notify_slack(self, chat: str) -> None:
        """Отправка уведомления в Slack."""
        try:
            response = self.slack_client.chat_postMessage(
                channel=self.slack_channel,
                text=f"Менеджер не ответил на сообщение в чате {chat}",
            )
            print(f"Slack уведомление отправлено: {response}")
        except SlackApiError as e:
            print(f"Ошибка при отправке сообщения в Slack: {e.response['error']}")

    async def check_chat_messages(self) -> None:
        """Проверяет последние сообщения в чатах и отправляет уведомления при необходимости."""
        for chat in self.chat_list:
            if chat in self.black_list:
                continue
            async for message in self.telegram_client.iter_messages(chat, limit=1):
                if not message:
                    continue
                if message.sender_id not in self.our_users_ids and not message.reactions:
                    if datetime.now() - message.date > timedelta(minutes=15):
                        await self.notify_slack(chat)

    async def check_chats(self) -> None:
        """Основной цикл проверки чатов."""
        while True:
            time_to_sleep, now = check_time()

            if not self.final_check_done and now.time() >= self.final_check_time:
                print("Запуск финального вечернего чека...")
                await self.check_chat_messages()
                self.final_check_done = True  # Отмечаем, что финальный чек выполнен

            if time_to_sleep:
                self.final_check_done = False  # Сбрасываем флаг утром
                await sleep_until_morning(now)

            await self.check_chat_messages()
            await asyncio.sleep(1800)  # Проверяем чаты каждые 30 минут