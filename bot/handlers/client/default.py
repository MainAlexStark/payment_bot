from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import Message

from aiogram.fsm.state import StatesGroup, State

import strings
from strings.en import strings

import os

from db import UserDataBase
from strings import en

import json

from payments.orders import orders
import time

from WalletPay import WalletPayAPI

router = Router()

db_client = UserDataBase('DB/users.db')

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):

    if message.chat.type == "private":

        # Получаем путь к текущему файлу temp.py
        current_path = os.path.abspath(__file__)

        # Формируем путь к файлу config.json
        config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

        user_name = message.from_user.first_name
        user_id = message.from_user.id

        # Проверяем, являеется ли пользователь новым
        is_user = db_client.is_user(user_id)

        sub_channel = {}
        sub_channel_flag = True

        not_sub_channel_str = ''

        buttons = []

        with open(config_path) as file:
            config = json.load(file)

            # # Initialize the API client
            # api = WalletPayAPI(api_key=config["WalletPay"]["TOKEN"])

            # print(orders.storage.keys())
            # for order_id in orders.storage.values():
            #     print('order=',api.get_order_preview(order_id))

            channels = []

            # Создаем кнопки с каналами
            for channel_name, channel_cost in config["channels"]["channels_cost"].items():
                user_channel_status = await message.bot.get_chat_member(chat_id=config['channels']['channels_id'][channel_name], user_id=message.from_user.id)
                if user_channel_status.status != 'left': 
                    continue

                sub_channel_flag = False
                channels.append([types.InlineKeyboardButton(text=f"{channel_name} - {config["payment"]["pay_wallet"]}{channel_cost} for {config["payment"]["subscription_duration"]} days",\
                                                        callback_data=f"pay={channel_name}")])
            
            channels_without_subscription = types.InlineKeyboardMarkup(inline_keyboard=channels)

        if is_user:
            if sub_channel_flag:
                # Если пользователь подписан на все каналы то выводим соответсвующее сообщение
                await message.answer(text=f"You are already subscribed to all channels")
            else:
                await message.answer(text="You can also subscribe to:", reply_markup=channels_without_subscription)
        else:
            # Добавляем пользователя в db
            db_client.add_user(user_id)

            buttons = []

            # Создаем пригласительные ссылки
            for channel_name, channel_id in config["channels"]["channels_id"].items():

                link = await message.bot.create_chat_invite_link(channel_id, member_limit=1)

                # Добавляем ссылки в клавиатуру
                buttons.append(types.InlineKeyboardButton(text=channel_name, url=link.invite_link))

            # Создаем клавиатуру с каналами, на которые нет подписки
            start_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons,])

            await message.answer(text=strings['start_message'],reply_markup=start_keyboard,parse_mode="HTML", disable_web_page_preview=True)



        if user_id in config['admins']:

            string = en.strings["start_message_admin"]

            for dict in config['commands']['admin'].values():
                for command in dict:
                    string += f"\n/{command}"
        
            await message.answer(string)




@router.message(Command("help"))
async def cmd_help(message: Message):

    if message.chat.type == "private":

        user_id = message.from_user.id

        # Получаем путь к текущему файлу temp.py
        current_path = os.path.abspath(__file__)

        # Формируем путь к файлу config.json
        config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

        # Открываем JSON файл
        with open(config_path) as file:
            config = json.load(file)

        if user_id in config['admins']:

            string = en.strings["start_message_admin"]

            for dict in config['commands']['admin'].values():
                for command in dict:
                    string += f"\n/{command}"
        
            await message.answer(string)
        else:
            string = en.strings["help_message"]

            for dict in config['commands']['user'].values():
                for command in dict:
                    string += f"\n/{command}"
        
            await message.answer(string)