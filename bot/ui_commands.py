from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_bot_commands(bot: Bot):
    commands = [
            BotCommand(command="start", description="Start"),
            BotCommand(command="status", description="Status"),
            BotCommand(command="products ", description="Products"),
            BotCommand(command="help", description="Help")
        ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())