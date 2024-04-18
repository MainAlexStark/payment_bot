""" third party imports """
import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import re
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart

""" internal imports """
from db import Config

from handlers.admin import stat, channels
from handlers.client import default, payment
from ui_commands import set_bot_commands

""" import tasks """
from tasks import check_end
from tasks import check_paid

""" OPEN CONFIG """
file_path = 'data/config.json'
if os.path.exists(file_path):
    config_client = Config(file_path)
    config = config_client.get()
else:
    raise Exception(f'File {file_path} not found')

""" tasks """
async def scheduled(bot ,sleep_for):
    while True:
        await check_end.check(bot)
        await asyncio.sleep(sleep_for)

async def paid_handler(bot, sleep_for):
    while True:
        await check_paid.check(bot)
        await asyncio.sleep(sleep_for)

async def main():
    logging.basicConfig(level=logging.WARNING)

    bot = Bot(config["bot"]["TOKEN"])

    storage = MemoryStorage()

    # Создание диспетчера
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров с хэндлерами
    dp.include_router(default.router)
    dp.include_router(stat.router)
    dp.include_router(channels.router)
    dp.include_router(payment.router)

    # Set bot commands in the UI
    await set_bot_commands(bot)

    # Отправьте асинхронную задачу для постоянной проверки окончания подписки или пробного периода на какой либо канал
    asyncio.create_task(scheduled(bot, 86400))  # 86400 секунд - это 24 часа
    asyncio.create_task(paid_handler(bot, 5))  # Проверяем оплату

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':

    print('BOT START')
    asyncio.run(main())