""" third party imports """
from aiogram import Bot
import os

""" internal imports """
from db import DataBaseInterface, Config

file_path = 'data/DataBase.db'
if os.path.exists(file_path):
    db = DataBaseInterface(file_path, "users")
else:
    raise Exception(f'File {file_path} not found')

file_path = 'data/strings.json'
if os.path.exists(file_path):
    config_client = Config(file_path)
    strings = config_client.get()
else:
    raise Exception(f'File {file_path} not found')

async def check(bot: Bot) -> None:
    """ We go through the ids of all users and perform the necessary actions """
    for user_id in db.get_users():
        await bot.send_message(user_id, strings['tasks']['main_example'])