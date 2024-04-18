""" third party imports """
import os
import random

from aiogram import Router, F, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext

from aiogram import Bot, Dispatcher
import time

from datetime import datetime, timedelta

import re

""" internal imports """
from db import Config, DataBaseInterface
from aiogram_interface import AiogramInterface
from payments.ton import TON
from payments.orders import orders

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

""" OPEN STRINGS """
file_path = 'data/config.json'
if os.path.exists(file_path):
    config_client = Config(file_path)
else:
    raise Exception(f'File {file_path} not found')


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery) -> None:
    await pre_checkout_q.answer(ok=True)

@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message) -> None:
    print('SUCCESSFUL_PAYMENT DEBUG')

    config = config_client.get()
    ai = AiogramInterface(message.bot)
    user_id = message.from_user.id

    num_purchases = db.get_column(user_id=user_id, column='num_purchases')

    channel_id = message.successful_payment.invoice_payload
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
        


    trial_period = config['payment']['free_trial']
    sub_period = config['payment']['subscription_duration']

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

    if message.successful_payment.invoice_payload == 'all':
        buttons = []
        for name, data in config['channels']['paid'].items():
            channel_id = data['id']
            await ai.unban_chat_member(channel_id=channel_id, user_id=user_id)

            db.change_data(user_id=user_id, column=name.replace(' ','_'), new_value=date_plus_diff_days)

            link = await ai.create_chat_invite_link(channel_id)

            buttons.append([types.InlineKeyboardButton(text=name, url=link)])

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(f'Payment for the all channel was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                            , reply_markup=keyboard)
        
    else:
        channel_name = ''

        for name, data in config['channels']['paid'].items():
                id = data['id']
                if id == str(channel_id):
                    channel_name = name

        buttons = []

        sub_period = config['payment']['subscription_duration']

        await ai.unban_chat_member(channel_id=channel_id, user_id=user_id)

        link = await ai.create_chat_invite_link(channel_id)

        db.change_data(user_id=user_id, column=channel_name.replace(' ','_'), new_value=date_plus_diff_days)

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=channel_name, url=link)]
        ])

        await message.answer(f'Payment for the {channel_name} was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                            , reply_markup=keyboard)
        





@router.callback_query()
async def general_start(callback: CallbackQuery, state: FSMContext):
    config = config_client.get()
    user_id = callback.from_user.id

    if callback.data.split('=')[0] == "pay":

        channel_name = callback.data.split('=')[1]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=f"Pay with card using Stripe", callback_data=f"stripe={channel_name}")],
            [types.InlineKeyboardButton(text=f"Pay with card or crypto using TON Pay", callback_data=f"ton={channel_name}")],
        ])

        cost = 0
        if channel_name == 'all':
            cost = 0
            for name, data in config['channels']['paid'].items():
                cost += float(data['cost'])

            num_purchases = db.get_column(user_id=user_id, column='num_purchases')

            cost = cost*0.8
            if num_purchases is not None:
                    num_refferals = db.get_column(user_id=user_id, column='ref_num')
                    if num_refferals is not None:
                        if num_refferals>5:num_refferals=5
                        for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))
            cost = int(round(cost, -1) - 1)

        # If pay one channel
        elif channel_name in config['channels']['paid'].keys():
            cost = config['channels']['paid'][channel_name]['cost']

            num_purchases = db.get_column(user_id=user_id, column='num_purchases')
            if num_purchases is not None:
                num_refferals = db.get_column(user_id=user_id, column='ref_num')
                if num_refferals is not None:
                    if num_refferals>5:num_refferals=5
                    for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))
            
        await callback.bot.send_message(chat_id=user_id, text=f"Your payment is ${round(float(cost),2)} for {config['payment']['subscription_duration']} days",
                                            reply_markup=keyboard)
            

    if callback.data.split('=')[0] == "stripe":

        channel_name = callback.data.split('=')[1]

        if channel_name == 'all':
            cost = 0
            photo_url = 'https://img.freepik.com/premium-photo/a-pile-of-white-kittens-with-blue-eyes_808092-6239.jpg'
            payload = 'all'
            for name, data in config['channels']['paid'].items(): cost += float(data['cost'])

            num_purchases = db.get_column(user_id=user_id, column='num_purchases')

            cost = cost*0.8
            if num_purchases is not None:
                    num_refferals = db.get_column(user_id=user_id, column='ref_num')
                    if num_refferals is not None:
                        if num_refferals>5:num_refferals=5
                        for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))
            cost = int(round(cost, -1) - 1)

        if channel_name in config['channels']['paid'].keys():
            data = config['channels']['paid'][channel_name]
            cost = data['cost']
            photo_url = data['img']
            payload = data['id']

            num_purchases = db.get_column(user_id=user_id, column='num_purchases')
            if num_purchases is not None:
                num_refferals = db.get_column(user_id=user_id, column='ref_num')
                if num_refferals is not None:
                    if num_refferals>5:num_refferals=5
                    for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))

        await callback.bot.send_invoice(
                                callback.from_user.id,
                                title=channel_name,
                                description=f'Activation of subscription to {channel_name}.',
                                provider_token=config['Stripe']['TOKEN'],
                                currency="usd",
                                photo_url=photo_url,
                                photo_width=416,
                                photo_height=234,
                                photo_size=416,
                                is_flexible=False,
                                prices=[types.LabeledPrice(label=f'Subscribe to the {str(config["payment"]["subscription_duration"])} days',
                                                            amount=int(float(round(float(cost),2))*100))], # Цена в копейках
                                start_parameter="one-month-subscription",
                                payload=payload)
        

    if callback.data.split('=')[0] == "ton":

        ton_client = TON(api_key=config["WalletPay"]["TOKEN"])

        channel_name = callback.data.split('=')[1]
        channel_id = ''

        for name, data in config['channels']['paid'].items(): 
            if name == channel_name: channel_id = data['id']

        if str(user_id) in orders.storage.keys():
                await callback.bot.send_message(chat_id=user_id, text=f"You already have payment link")
        else:
            def generate_key():
                key = ''
                for i in range(2):
                    key += str(random.randint(100, 999)) + '-'
                key += str(random.randint(100, 999))
                return key

            externalId = str(int(time.time()))

            if channel_name == 'all':
                cost = 0
                for name, data in config['channels']['paid'].items(): 
                    is_sub = db.get_column(user_id=user_id, column=name.replace(' ','_'))
                    if is_sub is not None:
                        cost += float(data['cost'])

                num_purchases = db.get_column(user_id=user_id, column='num_purchases')

                cost = cost*0.8
                if num_purchases is not None:
                        num_refferals = db.get_column(user_id=user_id, column='ref_num')
                        if num_refferals is not None:
                            if num_refferals>5:num_refferals=5
                            for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))
                cost = int(round(cost, -1) - 1)

            if channel_name in config['channels']['paid'].keys():
                cost = config['channels']['paid'][channel_name]['cost']

            
                num_purchases = db.get_column(user_id=user_id, column='num_purchases')
                if num_purchases is not None:
                    num_refferals = db.get_column(user_id=user_id, column='ref_num')
                    if num_refferals is not None:
                        if num_refferals>5:num_refferals=5
                        for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))


            order_data = ton_client.get_pay_link(user_id=str(user_id),
                                                            amount=str(round(float(cost),2)),
                                                            description=f'Payment for subscription to {channel_name} channel',
                                                            bot_url=config['bot']["url"],
                                                            externalId=externalId)
            
            order_link = order_data['payLink']
            order_id = order_data['id']
            
            if len(order_link) > 0:
                await callback.bot.send_message(chat_id=user_id, text=f"Your payment link: {order_link}. It will be valid for 5 minutes")

                if channel_name == 'all':
                    orders.add_element(str(user_id), str(order_id), 'all', 300)
                if channel_name in config['channels']['paid'].keys():
                    orders.add_element(str(user_id), str(order_id), channel_id, 300)

            else:
                await callback.bot.send_message(chat_id=user_id, text=f"Oops, there was a mistake. Try a different payment method, or try again later.")


            