import asyncio
import json
import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tasks import end_of_access
from handlers.admin import channels
from handlers.client import default
from ui_commands import set_bot_commands

# Открываем JSON файл
with open('config.json') as file:
    config = json.load(file)

# Асинхронная функция для запуска проверки дат каждые 24 часа
async def scheduled(bot ,sleep_for):
    while True:
        await asyncio.sleep(sleep_for)
        await end_of_access.check_trial_end(bot, config['days_notice'])

async def main():

    bot = Bot(config["TOKEN"])

    storage = MemoryStorage()

    # Создание диспетчера
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров с хэндлерами
    dp.include_router(channels.router)
    dp.include_router(default.router)

    # Set bot commands in the UI
    #await set_bot_commands(bot)

    # Отправьте асинхронную задачу для постоянной проверки окончания пробного периода
    asyncio.create_task(scheduled(bot, 86400))  # 86400 секунд - это 24 часа

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':

    try:
        print('BOT START')
        asyncio.run(main())
    except Exception as e:
        print(e)
