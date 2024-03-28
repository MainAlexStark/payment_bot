from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

import json

# Открываем JSON файл
with open('config.json') as file:
    data = json.load(file)

commands = []
for command in data['commands']['user']['default']:
    commands.append(BotCommand(command=command, description=""))

async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())