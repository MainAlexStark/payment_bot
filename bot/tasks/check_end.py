""" third party imports """
from aiogram import Bot
import os, json
from datetime import datetime, timedelta

""" internal imports """
from db import DataBaseInterface, Config
from handlers.client.default import get_not_sub_channels_keyboard

""" OPEN DataBase """
file_path = 'data/DataBase.db'
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
else:
    raise Exception(f'File {file_path} not found')

async def check(bot: Bot) -> None:
    config = config_client.get()
    now = datetime.now().strftime('%d.%m.%Y')
    """ We go through the ids of all users and perform the necessary actions """
    for user_id in db.get_users():
        
        free_trial = db.get_column(user_id=user_id, column='start_date')

        if free_trial is not None:
            message = f'We value our relationship and would like to inform you that your subscription will end in {config["payment"]["days_notice"]} days'
            date = datetime.strptime(free_trial, '%d.%m.%Y')

            keyboard = await get_not_sub_channels_keyboard(bot, user_id=user_id)

            date_obj = datetime.strptime(date, '%d.%m.%Y')
            date_plus_trial = date_obj + timedelta(days=config['payment']['free_trial'])
            today = datetime.today()

            if date_plus_trial.date() - timedelta(days=config['payment']['days_notice']) == today.date():
                await bot.send_message(user_id, text=message, reply_markup=keyboard)