from datetime import datetime, timedelta
from strings.en import strings
from keyboards.tasks.free_trial import free_trial_end_keyboard
from db import UserDataBase

from aiogram import types

import os, json
from WalletPay import WalletPayAPI
from payments.orders import orders

# Получаем путь к текущему файлу
current_path = os.path.abspath(__file__)

# Формируем путь к файлу config.json
config_path = os.path.join(os.path.dirname(current_path), '../config.json')

# Этот скрипт отправляет предупреждения об окончании подписки и банит пользователя, если срок подписки подошел к концу
async def check(bot):
    
    db_client = UserDataBase('DB/users.db')

    # Подключаемся к базе данных
    conn = db_client.connect()
    cursor = conn.cursor()

    print(orders.storage)

    # Получаем id всех пользовтелей
    cursor.execute('SELECT id FROM users')
    ids = cursor.fetchall()

    msg = 'A detailed technical review of key energy markets delivered through Telegram private channels with links to websites for extensive description, educational resources and full historic archives of our analysis'


    # Открываем JSON файл
    with open(config_path) as file:
        config = json.load(file)

        # Initialize the API client
        api = WalletPayAPI(api_key=config["WalletPay"]["TOKEN"])

    for user_id in ids:
        user_id = user_id[0]

        if str(user_id) in orders.storage.keys():

                # Get order preview
                order_preview = api.get_order_preview(order_id=orders.storage[str(user_id)]['value'])

                # Check if the order is paid
                if order_preview.status == "PAID":
                    if orders.storage['channel'] == 'all':
                        # Открываем JSON файл
                        with open(config_path) as file:
                            config = json.load(file)
                            buttons = []
                            # Получаем текущую дату
                            current_date = datetime.now().strftime("%d.%m.%Y")
                            for channel_name, channel_id in config['channels']['channels_id'].items():

                                # Разбан пользователя
                                await bot.unban_chat_member(channel_id, user_id)

                                # Вводим изменения в базу данных
                                db_client.change_data(user_id, channel_name.replace(' ','_'), current_date)
                                
                                link = await bot.create_chat_invite_link(channel_id, member_limit=1)

                                # Добавляем ссылки в клавиатуру
                                buttons.append([types.InlineKeyboardButton(text=f'{channel_name}', url=link.invite_link)])

                            # Создаем клавиатуру с каналами, на которые нет подписки
                            start_keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

                            await bot.send_message.answer(user_id, f'Payment for the all channel was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                                            , reply_markup=start_keyboard)
                            
                    else:
                        channel_id = int(orders.storage['channel'])
                        channel_name = ''

                        # Открываем JSON файл
                        with open(config_path) as file:
                            config = json.load(file)

                            for key, value in config['channels']['channels_id'].items():
                                if value == channel_id:
                                    channel_name = key

                        buttons = []

                        link = await bot.create_chat_invite_link(channel_id, member_limit=1)

                        # Добавляем ссылки в клавиатуру
                        buttons.append([types.InlineKeyboardButton(text=f'{channel_name}', url=link.invite_link)])

                        # Создаем клавиатуру с каналами, на которые нет подписки
                        start_keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

                        # Разбан пользователя
                        await bot.unban_chat_member(channel_id, user_id)

                        # Вводим изменения в базу данных
                        # Получаем текущую дату
                        current_date = datetime.now().strftime("%d.%m.%Y")

                        db_client.change_data(user_id, channel_name.replace(' ','_'), current_date)

                        await bot.send_message(user_id, f'Payment for the {channel_name} channel was successful!\nYour subscription will be valid for {config["payment"]["subscription_duration"]} days'
                                            , reply_markup=start_keyboard)

                        
            