import asyncio
import logging

import uvicorn
import uvloop
from fastapi import FastAPI
from sqladmin import Admin

from src.admin import admin_views
from src.admin.auth import authentication_backend
from src.db.session import sync_engine
from src.settings import settings, log
from src.client import ManagerNotifier
from src.slack_client import SlackClient
from src.telegram_client import TGClient


async def app_startup() -> None:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    admin = Admin(app, sync_engine, authentication_backend=authentication_backend)
    for view in admin_views:
        admin.add_view(view)
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=logging.INFO,
    )
    server = uvicorn.Server(config)
    await server.serve()

async def notificator_startup() -> None:
    try:
        uvloop.install()
        notifier = ManagerNotifier(
            telegram_client=TGClient(settings.TELEGRAM.PHONE_NUMBER.get_secret_value(), settings.TELEGRAM.TELEGRAM_API_ID, settings.TELEGRAM.TELEGRAM_API_HASH),
            slack_client=SlackClient(settings.SLACK.SLACK_TOKEN.get_secret_value(), settings.SLACK.SLACK_CHANNEL),
        )
        log.info("Запуск нотификатора")
        await notifier.start()
    except ValueError as exc:
        log.info("Необходимо заполнить или завершить заполнение .env файла")
    except Exception as exc:
        log.info(f"Произошла непредвиденная ошибка: {exc}")


async def main() -> None:
    tasks = [
        asyncio.create_task(
            app_startup(),
            name="app-task",
        ),
        asyncio.create_task(
            notificator_startup(),
            name="notificator-task",
        ),
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
