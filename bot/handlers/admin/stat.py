from aiogram import Router, F, types
from aiogram.filters import Command, CommandObject, CommandStart

import os

""" internal imports """
from db import Config, DataBaseInterface

router = Router()

""" OPEN DataBase """
file_path = 'data/Database.db'
if os.path.exists(file_path):
    db = DataBaseInterface(file_path, "users")
else:
    raise Exception(f'File {file_path} not found')

""" OPEN STRINGS """
file_path = 'data/strings.json'
if os.path.exists(file_path):
    strings_client = Config(file_path)
    strings = strings_client.get()
else:
    raise Exception(f'File {file_path} not found')

""" OPEN CONFIG """
file_path = 'data/config.json'
if os.path.exists(file_path):
    config_client = Config(file_path)
    config = config_client.get()
else:
    raise Exception(f'File {file_path} not found')

@router.message(Command("statistics"))
async def cmd_start(message: types.Message):
    # Private chat check 
    if message.chat.type == "private":
        user_id = message.from_user.id
        if user_id in config['admins']:
            num_users = len(db.get_users())

            await message.reply(f"Statistic:\nnum_users={num_users}")