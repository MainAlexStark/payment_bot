import asyncio
import json
import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import types 

from tasks import check_end, check_paid
from handlers.admin import channels
from handlers.client import default, payment
from ui_commands import set_bot_commands

# Открываем JSON файл
with open('config.json') as file:
    config = json.load(file)

# Асинхронная функция для запуска проверки дат каждые 24 часа
async def scheduled(bot ,sleep_for):
    while True:
        await check_end.check(bot)
        await asyncio.sleep(sleep_for)

async def paid_handler(bot, sleep_for):
    while True:
        await check_paid.check(bot)
        await asyncio.sleep(sleep_for)

async def main():

    orders = {}

    bot = Bot(config["bot"]["TOKEN"])

    #await bot.unban_chat_member(-1002066507370, 6525546927)
    #await bot.unban_chat_member(-1002103257297, 6525546927)

    user_channel_status = await bot.get_chat_member(chat_id=-1002066507370, user_id=6525546927)

    # Если пользователь подписан на канал
    #print(user_channel_status.status)

    #user_channel_status = await bot.get_chat_member(-1002066507370, 6525546927)
    #print(user_channel_status.status)

    storage = MemoryStorage()

    # Создание диспетчера
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров с хэндлерами
    dp.include_router(channels.router)
    dp.include_router(default.router)
    dp.include_router(payment.router)

    # Set bot commands in the UI
    #await set_bot_commands(bot)

    # Отправьте асинхронную задачу для постоянной проверки окончания подписки или пробного периода на какой либо канал
    asyncio.create_task(scheduled(bot, 86400))  # 86400 секунд - это 24 часа
    asyncio.create_task(paid_handler(bot, 300))  # Проверяем оплату

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':


    print('BOT START')
    asyncio.run(main())
    # except Exception as e:
    #     print(e)
