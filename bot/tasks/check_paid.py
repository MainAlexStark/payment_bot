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
from payments.ton import TON

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
else:
    raise Exception(f'File {file_path} not found')



async def check(bot: Bot):
    ai = AiogramInterface(bot)
    config = config_client.get()
    api = TON(api_key=config["WalletPay"]["TOKEN"])

    #print(f"TON ORDERS={orders.storage}")

    for user_id in db.get_users():
        try:
            if str(user_id) in orders.storage.keys():
                order_preview_status = api.get_order_preview(order_id=orders.storage[str(user_id)]['value'])


                if order_preview_status == "PAID":

                    num_purchases = db.get_column(user_id=user_id, column='num_purchases')

                    channel_id = int(orders.storage[str(user_id)]['channel'])
                    channel_name = ''

                    for name, data in config['channels']['paid'].items():
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
                    num_purchases = db.get_column(user_id=user_id, column='num_purchases')

                    if ref_id is not None and num_purchases==1:
                        referrals = db.get_column(user_id=ref_id, column='ref_num')
                        if referrals is None: referrals = 0
                        if not db.change_data(user_id=ref_id, column='ref_num', new_value=referrals+1):
                            print(f'Error change num referrals. user_id ={user_id}, num referrals = {referrals}')
                        
                    sub_date = db.get_column(user_id=user_id, column=channel_name.replace(' ','_'))

                    trial_period = config['payment']['free_trial']
                    sub_period = config['payment']['subscription_duration']

                    trial_date = db.get_column(user_id=user_id, column='start_date')
                    if sub_date is not None:
                        date = datetime.strptime(sub_date, "%d.%m.%Y")
                        date_plus_subscription_duration = date + timedelta(days=int(sub_period))
                        date_plus_diff_days = date_plus_subscription_duration.strftime("%d.%m.%Y")
                    elif trial_date is not None:
                        date = datetime.strptime(trial_date, "%d.%m.%Y")
                        date_plus_trial_period = date + timedelta(days=int(trial_period))
                        date_plus_diff_days = date_plus_trial_period.strftime("%d.%m.%Y")
                    else:
                        date_plus_diff_days = datetime.now().strftime("%d.%m.%Y")

                    if channel_id == 'all':
                        buttons = []
                        for name, data in config['channels']['paid'].items():
                            channel_id = data['id']
                            await ai.unban_chat_member(channel_id=channel_id, user_id=user_id)

                            sub_date = db.get_column(user_id=user_id, column=name.replace(' ','_'))

                            trial_date = db.get_column(user_id=user_id, column='start_date')
                            if sub_date is not None:
                                date = datetime.strptime(sub_date, "%d.%m.%Y")
                                date_plus_subscription_duration = date + timedelta(days=int(sub_period))
                                date_plus_diff_days = date_plus_subscription_duration.strftime("%d.%m.%Y")
                            elif trial_date is not None:
                                date = datetime.strptime(trial_date, "%d.%m.%Y")
                                date_plus_trial_period = date + timedelta(days=int(trial_period))
                                date_plus_diff_days = date_plus_trial_period.strftime("%d.%m.%Y")
                            else:
                                date_plus_diff_days = datetime.now().strftime("%d.%m.%Y")

                            db.change_data(user_id=user_id, column=name.replace(' ','_'), new_value=date_plus_diff_days)
                            db.change_data(user_id=user_id, column='start_date', new_value=None)

                            link = await ai.create_chat_invite_link(channel_id)

                            buttons.append([types.InlineKeyboardButton(text=name, url=link)])

                        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

                        await bot.send_message(chat_id=user_id, text=f'Payment for the all channel was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                                            , reply_markup=keyboard)
                        
                    else:
                        channel_name = ''

                        for name, data in config['channels']['paid'].items():
                                id = data['id']
                                if id == str(channel_id):
                                    channel_name = name

                        buttons = []

                        await ai.unban_chat_member(channel_id=channel_id, user_id=user_id)

                        link = await ai.create_chat_invite_link(channel_id)

                        print(f"sub_date={sub_date}")

                        db.change_data(user_id=user_id, column=channel_name.replace(' ','_'), new_value=date_plus_diff_days)
                        db.change_data(user_id=user_id, column='start_date', new_value=None)

                        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text=channel_name, url=link)]
                        ])

                        await bot.send_message(chat_id=user_id, text=f'Payment for the {channel_name} was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                                            , reply_markup=keyboard)
                        
                    del orders.storage[str(user_id)]

        except Exception as e:
            print(f'Error get order preview. Error: {e}')
            if orders.storage[str(user_id)]['errors'] == 0:
                await bot.send_message(chat_id=user_id, text=f"Oops, an error occurred, wait for 5 minutes, and if the problem is not solved, contact support")

                for id in config["admins"]:
                    await bot.send_message(chat_id=id ,text=f"Failed to verify {user_id} payment. Error: {e}")

                orders.storage[str(user_id)]['errors'] = 1
                