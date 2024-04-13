""" third party imports """
from aiogram import Bot, types
import os, json
from datetime import datetime, timedelta
from WalletPay import WalletPayAPI

""" internal imports """
from db import DataBaseInterface, Config
from handlers.client.default import get_not_sub_channels_keyboard
from aiogram_interface import AiogramInterface
from payments.orders import orders

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



async def check(bot: Bot):
    ai = AiogramInterface(bot)
    config = config_client.get()
    api = WalletPayAPI(api_key=config["WalletPay"]["TOKEN"])

    for user_id in db.get_users():
        try:
            if str(user_id) in orders.storage.keys():
                order_preview = api.get_order_preview(order_id=orders.storage[str(user_id)]['value'])

                if order_preview.status == "PAID":

                    num_purchases = db.get_column(user_id=user_id, column='num_purchases')

                    channel_id = int(orders.storage['channel'])
                    channel_name = ''

                    for name, data in config['channels']['paid'].items:
                        if str(channel_id) == data['id']: channel_name=name

                    if num_purchases is not None:
                        referrals = db.get_column(user_id=user_id, column='num_purchases')
                        if num_purchases is None: referrals = 0
                        if not db.change_data(user_id=user_id, column='num_purchases', new_value=num_purchases+1):
                            print(f'Error change num_purchases. user_id ={user_id}, num_purchases = {num_purchases}')
                    else:
                        if not db.change_data(user_id=user_id, column='num_purchases', new_value=1):
                            print(f'Error change num_purchases. user_id ={user_id}, num_purchases = {num_purchases}')

                    ref_id = db.get_column(user_id=user_id, column='ref_id')

                    if ref_id is not None:
                        referrals = db.get_column(user_id=ref_id, column='ref_num')
                        if referrals is None: referrals = 0
                        if not db.change_data(user_id=ref_id, column='ref_num', new_value=referrals+1):
                            print(f'Error change num referrals. user_id ={user_id}, num referrals = {referrals}')
                        


                    trial_period = config['payment']['free_trial']
                    sub_period = config['payment']['subscription_duration']

                    trial_date = db.get_column(user_id=user_id, column='start_date')
                    sub_date = db.get_column(user_id=user_id, column=channel_name.replace(' ','_'))
                    if trial_date is not None:
                        date = datetime.strptime(trial_date, "%d.%m.%Y")
                        date_plus_subscription_duration = date + timedelta(days=int(trial_period))
                        diff = date_plus_subscription_duration - datetime.now()
                        diff_days = int(str(diff.days))
                        date_plus_diff = date + timedelta(days=diff_days)
                        date_plus_diff_days = date_plus_diff.strftime("%d.%m.%Y")
                    elif sub_date is not None:
                        date = datetime.strptime(sub_date, "%d.%m.%Y")
                        date_plus_subscription_duration = date + timedelta(days=int(sub_period))
                        diff = date_plus_subscription_duration - datetime.now()
                        diff_days = int(str(diff.days))
                        date_plus_diff = date + timedelta(days=diff_days)
                        date_plus_diff_days = date_plus_diff.strftime("%d.%m.%Y")
                    else:
                        date_plus_diff_days = datetime.now().strftime("%d.%m.%Y")

                    if orders.storage['channel'] == 'all':
                        buttons = []
                        for name, data in config['channels']['paid'].items():
                            channel_id = data['id']
                            await ai.unban_chat_member(channel_id=channel_id, user_id=user_id)

                            db.change_data(user_id=user_id, column=name.replace(' ','_'), new_value=date_plus_diff_days)

                            link = await ai.create_chat_invite_link(channel_id)

                            buttons.append([types.InlineKeyboardButton(text=name, url=link)])

                        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

                        await bot.send_message(chat_id=user_id, text=f'Payment for the all channel was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                                            , reply_markup=keyboard)
                    else:

                        buttons = []

                        await ai.unban_chat_member(channel_id=channel_id, user_id=user_id)

                        link = await ai.create_chat_invite_link(channel_id)

                        db.change_data(user_id=user_id, column=channel_name.replace(' ','_'), new_value=date_plus_diff_days)

                        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text=channel_name, url=link)]
                        ])

                        await bot.send_message(chat_id=user_id, text=f'Payment for the all channel was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                                            , reply_markup=keyboard)

        except Exception as e:
            print(f'Error get order preview. Error: {e}')