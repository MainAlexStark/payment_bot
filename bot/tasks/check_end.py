""" third party imports """
from aiogram import Bot
import os, json
from datetime import datetime, timedelta

""" internal imports """
from db import DataBaseInterface, Config
from handlers.client.default import get_not_sub_channels_keyboard
from aiogram_interface import AiogramInterface
from handlers.client.default import get_all_paid_keyboard

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
    ai = AiogramInterface(bot)
    config = config_client.get()
    """ We go through the ids of all users and perform the necessary actions """
    for user_id in db.get_users():
        print(user_id)
        
        free_trial = db.get_column(user_id=user_id, column='start_date')

        if free_trial is not None:
            message = f'We value our relationship and would like to inform you that your subscription will end in {config["payment"]["days_notice"]} days'
            message_end = f'We are sorry to have you go. If you decide to get back we will be happy to see you again'

            keyboard = await get_not_sub_channels_keyboard(bot, user_id=user_id)

            date_obj = datetime.strptime(free_trial, '%d.%m.%Y')
            date_plus_trial = date_obj + timedelta(days=int(config['payment']['free_trial']))
            today = datetime.today()

            print(f'date_plus_trial={date_plus_trial}')

            if date_plus_trial.date() - timedelta(days=int(config['payment']['days_notice'])) == today.date():
                await bot.send_message(user_id, text=message, reply_markup=keyboard)

            if date_plus_trial.date() <= today.date():
                db.change_data(user_id=user_id, column='start_date', new_value=None)
                print(f'ban user. End free trial. date={date_plus_trial.date()}')
                for channel_name, data in config['channels']['paid'].items():
                    id = data['id']
                    if db.get_column(user_id=user_id, column=channel_name.replace(' ','_')) is None:
                        res = await ai.ban_chat_member(channel_id=id, user_id=user_id)
                        if not res: ai.msg_to_admins(f"Error ban member: {user_id}")
                await bot.send_message(user_id, text=message_end, reply_markup=keyboard)
        else:
            keyboard = await get_all_paid_keyboard(bot=bot, user_id=user_id)
            channels_nof = 'To channels:'
            channels_ban = 'To channels:'
            for channel_name, data in config['channels']['paid'].items():
                    id = data['id']
                    user_channel_status = await ai.get_chat_member(channel_id=id, user_id=user_id)

                    message = f'We value our relationship and would like to inform you that your subscription will end in {config["payment"]["days_notice"]} days'
                    message_end = f'We are sorry to have you go. If you decide to get back we will be happy to see you again'

                    channels_date = db.get_column(user_id=user_id, column=channel_name.replace(' ','_'))
                    if channels_date is not None:

                        date_obj = datetime.strptime(channels_date, '%d.%m.%Y')
                        date_plus_sub = date_obj + timedelta(days=int(config['payment']['subscription_duration']))
                        today = datetime.today()

                        if date_plus_sub.date() - timedelta(days=int(config['payment']['days_notice'])) == today.date():
                            await bot.send_message(user_id, text=message, reply_markup=keyboard)

                        if date_plus_sub.date() <= today.date():
                            print(f'ban user. End subcr. date={date_plus_sub.date()}')
                            if await ai.ban_chat_member(channel_id=id, user_id=user_id): 
                                db.change_data(user_id=user_id, column=channel_name.replace(' ','_'), new_value=None)
                                await bot.send_message(user_id, text=message_end, reply_markup=keyboard)
                            else: ai.msg_to_admins(f"Error ban member: {user_id}")

                        if free_trial is None and channels_date is None and user_channel_status != 'left' and user_channel_status != 'kicked':
                            try:
                                print(f'Бан пользователя id={user_id}. Пользователь без подписки')
                                await ai.ban_chat_member(channel_id=id, user_id=user_id)
                            except Exception as e:
                                print(f'Не удалось заблокировать пользователя {user_id}\tError={e}')