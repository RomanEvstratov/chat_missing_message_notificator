import asyncio
from datetime import datetime, timedelta

from src.db.repo import NotificatorRepository
from src.db.session import async_session
from src.exceptions import DefaultException
from src.settings import settings, log
from src.slack_client import SlackClient
from src.telegram_client import TGClient


class ManagerNotifier:
    woke_up_time = datetime.strptime(settings.NOTIFICATOR.TIME_TO_WOKE_UP, "%H:%M").time()
    sleeping_time = datetime.strptime(settings.NOTIFICATOR.TIME_TO_SLEEP, "%H:%M").time()
    final_check_done = False  # Флаг для предотвращения повторного финального чека

    def __init__(
        self,
        telegram_client: TGClient,
        slack_client: SlackClient,
    ) -> None:
        self.tg_client = telegram_client
        self.slack_client = slack_client

    async def check_chat_messages(self) -> None:
        """Проверяет последние сообщения в чатах и отправляет уведомления при необходимости."""
        try:
            async with async_session() as session:
                blacklist = await NotificatorRepository.get_blacklisted_chats(session)
                approved_users = await NotificatorRepository.get_our_users(session)
            chats = await self.tg_client.check_chat_messages(blacklist, approved_users)
            if chats:
                log.info(f"Не было подано обратной связи для {len(chats)} диалогам")
                return await self.slack_client.notify_about_chat(chats)
            log.info("Не было найдено проигнорированных диалогов")
        except DefaultException as exc:
            log.info(f"{exc}")
            raise DefaultException from exc
        except Exception as exc:
            log.info(f"{exc}")

    async def start_session(self):
        connect = await self.tg_client.connect()
        if not connect:
            log.info("Подключиться к сессии не получилось")
            phone_code_hash = await self.tg_client.send_code()
            if phone_code_hash:
                await self.slack_client.send_slack_message("Необходимо ввести код доступа")
            await self.tg_client.sign_in(phone_code_hash)

    async def check_chats(self) -> None:
        """Основной цикл проверки чатов."""
        while True:
            try:
                time_to_sleep, now = self._check_time()
                if not self.final_check_done and (now.time() < self.woke_up_time or now.time() >= self.sleeping_time):
                    log.info("Запуск финальной вечерней проверки...")
                    await self.start_session()
                    await self.check_chat_messages()
                    self.final_check_done = True  # Отмечаем, что финальный чек выполнен

                if time_to_sleep:
                    self.final_check_done = False  # Сбрасываем флаг утром
                    await self.tg_client.disconnect()
                    await self._sleep_until_morning(now)
                else:
                    await asyncio.sleep(settings.NOTIFICATOR.TIME_BETWEEN_CHECK)

                await self.start_session()
                await self.check_chat_messages()
            except DefaultException as exc:
                await self.start_session()
            except Exception as exc:
                log.info(f"{exc}")
            finally:
                await self.tg_client.disconnect()

    async def start(self):
        me = await self.tg_client.login()
        if me:
            log.info("Присутствует соединение с сессией")
            await self.tg_client.disconnect()
            await self.check_chats()

    @classmethod
    async def _sleep_until_morning(cls, now: datetime) -> None:
        tomorrow = now.date() + timedelta(days=1)
        wake_time = datetime.combine(tomorrow, cls.woke_up_time)

        sleep_seconds = (wake_time - now).total_seconds()
        log.info(
            f"Пробуждение через ({sleep_seconds:.0f} секунд)"
        )
        await asyncio.sleep(sleep_seconds)
        log.info("Пробуждение", datetime.now().strftime("%H:%M"))

    @classmethod
    def _check_time(cls) -> tuple[bool, datetime]:
        now = datetime.now()
        current_time = now.time()
        if cls.woke_up_time < current_time < cls.sleeping_time:
            return False, now
        return True, now