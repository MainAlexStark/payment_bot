from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from aiogram.fsm.state import StatesGroup, State

from aiogram import types, F, Bot

from datetime import datetime, timedelta


import os,json, requests

from db import UserDataBase
from payments.ton import TON

from payments.orders import orders
import time

from WalletPay import WalletPayAPI

buttons = [
    [types.InlineKeyboardButton(text='exit',callback_data='exit')]
]
keyboard_back = types.InlineKeyboardMarkup(inline_keyboard=buttons)

router = Router()

db_client = UserDataBase('DB/users.db')

@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery) -> None:
    await pre_checkout_q.answer(ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message) -> None:

    # Получаем путь к текущему файлу temp.py
    current_path = os.path.abspath(__file__)

    # Формируем путь к файлу config.json
    config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

    user_id = message.from_user.id

    if message.successful_payment.invoice_payload == 'all':
        # Открываем JSON файл
        with open(config_path) as file:
            config = json.load(file)
            buttons = []
            # Получаем текущую дату
            current_date = datetime.now().strftime("%d.%m.%Y")
            for channel_name, channel_id in config['channels']['channels_id'].items():

                # Разбан пользователя
                await message.bot.unban_chat_member(channel_id, user_id)

                # Вводим изменения в базу данных
                db_client.change_data(user_id, channel_name.replace(' ','_'), current_date)
                
                link = await message.bot.create_chat_invite_link(channel_id, member_limit=1)

                # Добавляем ссылки в клавиатуру
                buttons.append([types.InlineKeyboardButton(text=f'{channel_name}', url=link.invite_link)])

            # Создаем клавиатуру с каналами, на которые нет подписки
            start_keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

            await message.answer(f'Payment for the all channel was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                            , reply_markup=start_keyboard)
            
    else:

        channel_id = int(message.successful_payment.invoice_payload)
        channel_name = ''

        # Открываем JSON файл
        with open(config_path) as file:
            config = json.load(file)

            for key, value in config['channels']['channels_id'].items():
                if value == channel_id:
                    channel_name = key

        buttons = []

        link = await message.bot.create_chat_invite_link(channel_id, member_limit=1)

        # Добавляем ссылки в клавиатуру
        buttons.append([types.InlineKeyboardButton(text=f'{channel_name}', url=link.invite_link)])

        # Создаем клавиатуру с каналами, на которые нет подписки
        start_keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        # Разбан пользователя
        await message.bot.unban_chat_member(channel_id, user_id)

        # Вводим изменения в базу данных
        # Получаем текущую дату
        current_date = datetime.now().strftime("%d.%m.%Y")

        db_client.change_data(user_id, channel_name.replace(' ','_'), current_date)

        await message.answer(f'Payment for the {channel_name} channel was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                            , reply_markup=start_keyboard)

@router.callback_query()
async def general_start(callback: CallbackQuery, state: FSMContext):

    user_name = callback.from_user.first_name
    user_id = callback.from_user.id

    # Получаем путь к текущему файлу temp.py
    current_path = os.path.abspath(__file__)

    # Формируем путь к файлу config.json
    config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

    if callback.data.split('=')[0] == "pay":
    
        callback_data = callback.data.split('=')[1]

        buttons = [
            [types.InlineKeyboardButton(text='Pay with card using Stripe',callback_data=f'stripe={callback_data}')],
            [types.InlineKeyboardButton(text='Pay with card or crypto using TON Pay',callback_data=f'ton={callback_data}')],
            #[types.InlineKeyboardButton(text='Pay with card using SBER',callback_data=f'sber={callback_data}')],
        ]

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        # Открываем JSON файл
        with open(config_path) as file:
            config = json.load(file)

            if callback_data == 'all':
                all_cost = 0
                for channel_cost in config["channels"]["channels_cost"].values(): all_cost += int(channel_cost)

                wallet = config["payment"]["pay_wallet"]
                dur = config["payment"]["subscription_duration"]
                await callback.bot.send_message(chat_id=user_id, text=f"Your payment is {wallet}{all_cost} for {dur} days", reply_markup=keyboard)

            if callback_data in config["channels"]["channels_cost"].keys():
                cost = config["channels"]["channels_cost"][callback_data]
                wallet = config["payment"]["pay_wallet"]
                dur = config["payment"]["subscription_duration"]

                await callback.bot.send_message(chat_id=user_id, text=f"Your payment is {wallet}{cost} for {dur} days", reply_markup=keyboard)

    if callback.data.split('=')[0] == "ton":

        callback_data = callback.data.split('=')[1]        

        # Открываем JSON файл
        with open(config_path) as file:
            config = json.load(file)

            # Initialize the API client
            ton_client = TON(api_key=config["WalletPay"]["TOKEN"])
            # Initialize the API client
            api = WalletPayAPI(api_key=config["WalletPay"]["TOKEN"])

            if str(user_id) in orders.storage.keys():
                await callback.bot.send_message(chat_id=user_id, text=f"You already have payment link")
            else:
                externalId = str(time.time())

                if callback_data == all:
                    all_cost = 0
                    orders.add_element(str(user_id), externalId, 'all', 300)  # Добавляем элемент, который удалится через 300 секунд
                    for channel_cost in config["channels"]["channels_cost"].values(): all_cost += int(channel_cost)
                    order_link = ton_client.get_pay_link(user_id=str(user_id),
                                                            amount=str(all_cost),
                                                            description=f'Payment for subscription to {callback_data} channel',
                                                            bot_url=config['bot']["url"],
                                                            externalId=externalId)
                else:
                    orders.add_element(str(user_id), externalId, str(config['channels']['channels_id'][callback_data]), 300)  # Добавляем элемент, который удалится через 300 секунд
                    order_link = ton_client.get_pay_link(user_id=str(user_id),
                                                            amount=config["channels"]['channels_cost'][callback_data],
                                                            description=f'Payment for subscription to {callback_data} channel',
                                                            bot_url=config['bot']["url"],
                                                            externalId=externalId)

                if len(order_link) > 0: 
                    await callback.bot.send_message(chat_id=user_id, text=f"Your payment link: {order_link}. It will be valid for 5 minutes")
                else:
                    print('Ошибка при создании сссылки для оплаты WalletPay')


        #print(api.get_order_preview(externalId))


    if callback.data.split('=')[0] == "stripe":

        callback_data = callback.data.split('=')[1]

        # Открываем JSON файл
        with open(config_path) as file:
            config = json.load(file)

            if callback_data == 'all':
                all_cost = 0
                for channel_cost in config["channels"]["channels_cost"].values(): all_cost += int(channel_cost)
                await callback.bot.send_invoice(
                                callback.from_user.id,
                                title=callback_data,
                                description=f"Activation of subscription to {callback_data}",
                                provider_token=config['Stripe']['TOKEN'],
                                currency="usd",
                                photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                                photo_width=416,
                                photo_height=234,
                                photo_size=416,
                                is_flexible=False,
                                prices=[types.LabeledPrice(label=f'Subscribe to the {str(config["payment"]["subscription_duration"])} days',
                                                            amount=int(float(all_cost)*100))], # Цена в копейках
                                start_parameter="one-month-subscription",
                                payload='all')
            else:
                await callback.bot.send_invoice(
                                callback.from_user.id,
                                title=callback_data,
                                description=f'Activation of subscription to {callback_data}.\n{config["channels"]["channels_description"][callback_data]}',
                                provider_token=config['Stripe']['TOKEN'],
                                currency="usd",
                                photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                                photo_width=416,
                                photo_height=234,
                                photo_size=416,
                                is_flexible=False,
                                prices=[types.LabeledPrice(label=f'Subscribe to the {str(config["payment"]["subscription_duration"])} days',
                                                            amount=int(float(config['channels']['channels_cost'][callback_data])*100))], # Цена в копейках
                                start_parameter="one-month-subscription",
                                payload=str(config['channels']['channels_id'][callback_data]))
                



    if callback.data.split('=')[0] == "sber":

        callback_data = callback.data.split('=')[1]

        # Открываем JSON файл
        with open(config_path) as file:
            config = json.load(file)

            if callback_data == 'all':
                all_cost = 0
                for channel_cost in config["channels"]["channels_cost"].values(): all_cost += int(channel_cost)
                await callback.bot.send_invoice(
                                callback.from_user.id,
                                title=callback_data,
                                description=f"Activation of subscription to {callback_data}",
                                provider_token=config['Sber']['TOKEN'],
                                currency="usd",
                                photo_url=config["channels"]["channels_img_url"][callback_data],
                                photo_width=416,
                                photo_height=234,
                                photo_size=416,
                                is_flexible=False,
                                prices=[types.LabeledPrice(label=f'Subscribe to the {str(config["payment"]["subscription_duration"])} days',
                                                            amount=int(float(all_cost)*100))], # Цена в копейках
                                start_parameter="one-month-subscription",
                                payload='all')
            else:
                await callback.bot.send_invoice(
                                callback.from_user.id,
                                title=callback_data,
                                description=f"Activation of subscription to {callback_data}.\n{config['channels']['channels_description'][callback_data]}",
                                provider_token=config['Sber']['TOKEN'],
                                currency="usd",
                                photo_url=config["channels"]["channels_img_url"][callback_data],
                                photo_width=416,
                                photo_height=234,
                                photo_size=416,
                                is_flexible=False,
                                prices=[types.LabeledPrice(label=f'Subscribe to the {str(config["payment"]["subscription_duration"])} days',
                                                            amount=int(float(config['channels']['channels_cost'][callback_data])*100))], # Цена в копейках
                                start_parameter="one-month-subscription",
                                payload=str(config['channels']['channels_id'][callback_data]))