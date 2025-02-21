from datetime import datetime, timedelta

import asyncio

from app.settings import TIME_TO_SLEEP, TIME_TO_WOKE_UP


async def sleep_until_morning(now: datetime) -> None:
    tomorrow = now.date() + timedelta(days=1)
    wake_time = datetime.combine(
        tomorrow, datetime.strptime(TIME_TO_WOKE_UP, "%H:%M").time()
    )

    sleep_seconds = (wake_time - now).total_seconds()
    print(
        f"Я слабый, мне нужно много спать и в волю есть, до 09:00... ({sleep_seconds:.0f} секунд)"
    )
    await asyncio.sleep(sleep_seconds)
    print("Пора просыпаться... Время:", datetime.now().strftime("%H:%M"))


def check_time() -> tuple[bool, datetime]:
    now = datetime.now()
    current_time = now.time()
    if current_time >= datetime.strptime(TIME_TO_SLEEP, "%H:%M").time():
        return True, now
    return False, now
