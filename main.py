import asyncio
from telethon import TelegramClient
from slack_sdk import WebClient as SlackClient

from app import settings
from app.client import ManagerNotifier


async def main() -> None:
    telegram_client = TelegramClient(
        settings.PHONE_NUMBER, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH
    )
    slack_client = SlackClient(token=settings.SLACK_TOKEN)
    telegram_client.start()

    notifier = ManagerNotifier(
        telegram_client=telegram_client,
        slack_client=slack_client,
        slack_channel=settings.SLACK_CHANNEL,
        chat_list=settings.CHAT_LIST,
        black_list=settings.CHAT_BLACK_LIST,
        our_users_ids=settings.MANAGERS_IDS,
    )

    await notifier.check_chats()



if __name__ == "__main__":
    asyncio.run(main())
