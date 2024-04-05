from datetime import datetime, timedelta
from strings.en import strings
from db import UserDataBase

from aiogram import types

import os, json


# Этот скрипт отправляет предупреждения об окончании подписки и банит пользователя, если срок подписки подошел к концу
async def check(bot):
    # Получаем путь к текущему файлу
    current_path = os.path.abspath(__file__)

    # Формируем путь к файлу config.json
    config_path = os.path.join(os.path.dirname(current_path), '../config.json')

    # Открываем JSON файл
    with open(config_path) as file:
        config = json.load(file)

        db = UserDataBase('DB/users.db')

        # Подключаемся к базе данных
        conn = db.connect()
        cursor = conn.cursor()

        # Получаем id всех пользовтелей
        cursor.execute('SELECT id FROM users')
        values = cursor.fetchall()

        print(f'number of users={len(values)}')

        now = datetime.now().strftime('%d.%m.%Y')

        # Перебираем всех пользователей по id
        for user_id in values:

            user_id = user_id[0]
            
            # получаем данные о пользователе
            user_data = db.get_data(user_id)

            
    ##################### Изменить на поиск подписки по базе данных
            # Получаем словарь каналов на которые у пользователя нет подписки
            not_sub_channels = {}
            for channel_name, channel_id in config['channels']['channels_id'].items():
                user_channel_status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                if user_channel_status.status != 'left': 
                    continue
                not_sub_channels[channel_name] = channel_id


            # Открываем JSON файл
            with open(config_path) as file:
                config = json.load(file)

                channels = []

                # Создаем кнопки с каналами
                for channel_name, channel_id in not_sub_channels.items():
                    channels.append([types.InlineKeyboardButton(text=f"{channel_name} - {config["payment"]["pay_wallet"]}{config['channels']['channels_cost'][channel_name]} for {config["payment"]["subscription_duration"]} days",\
                                                            callback_data=f"pay={channel_name}")])
                
                free_trial_end_keyboard = types.InlineKeyboardMarkup(inline_keyboard=channels)


            # Узнаем, идет ли пробный период
            if user_data[1] == 1:
                
                # Получаем дату и приводим к нужному формату
                date_str = user_data[2]
                date = datetime.strptime(date_str, '%d.%m.%Y')

                # Создаем сообщение
                message = strings['before_end_free_trial']
                i = 1
                for des in config["channels"]['channels_description'].values():
                    message += f'\n{i}. {des}'
                    i += 1

                # Отправляем сообщение пользователям
                #print(f"предупреждение о конец бесплатной версии {date + timedelta(days=config['payment']["trial_period"]) - timedelta(days=config["payment"]["days_notice"])}")
                #print(f"конец бесплатной версии {date + timedelta(days=config['payment']["trial_period"])}")
                if datetime.strptime(now, '%d.%m.%Y') == date + timedelta(days=config['payment']["trial_period"]) - timedelta(days=config["payment"]["days_notice"]):
                    await bot.send_message(chat_id=user_id, text=message, reply_markup=free_trial_end_keyboard)

                message = strings['end_free_trial']
                # Баним пользователей
                if  datetime.strptime(now, '%d.%m.%Y') >= date + timedelta(days=config["payment"]["trial_period"]):
                    for channel_id in config["channels"]["channels_id"].values():
                        print(f'Бан пользователя id={user_id} по причине конца пробного периода')

                        try:
                            await bot.ban_chat_member(channel_id, user_id)
                        except Exception as e:
                            print(f'Не удалось заблокировать пользователя {user_id}\tError={e}')

                        db.change_data(user_id, "free_trial", False)

                    await bot.send_message(chat_id=user_id,text=message,reply_markup=free_trial_end_keyboard)

            # Проверяем, идет ли подписка на определенные каналы        
            for channel_name, channel_id in config["channels"]["channels_id"].items():

                channel_column = channel_name.replace(' ','_')

                date_channel = db.get_column(user_id, channel_column)

                message = f"We value our relationship and would like to inform you that your subscription will end in {str(config["payment"]["days_notice"])} days."

                buttons = [
                    [types.InlineKeyboardButton(text="Renew the subscription", callback_data=f"pay={channel_name}")],
                    [types.InlineKeyboardButton(text="Show me all subscription options", callback_data=f"show_subscription_options")],
                ]
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

                # Если пользователь имеет подписку
                if date_channel is not None:
                    # Получаем дату и приводим к нужному формату
                    date_str = date_channel
                    date = datetime.strptime(date_str, '%d.%m.%Y')

                    # Отправляем сообщение пользователям
                    if datetime.strptime(now, '%d.%m.%Y') == date + timedelta(days=config["payment"]["subscription_duration"]) - timedelta(days=config["payment"]["days_notice"]):
                        await bot.send_message(chat_id=user_id, text=message, reply_markup=keyboard)

                    # Баним пользователей
                    if datetime.strptime(now, '%d.%m.%Y') >= date + timedelta(days=config["payment"]["subscription_duration"]):
                        print(f'Бан пользователя id={user_id} по причине конца подписки на канал {channel_name}')
                        await bot.ban_chat_member(channel_id, user_id)
                        db.change_data(user_id, channel_column, None)

                        message = '“We value our relationship and would like to inform you that your subscription has ended today.'

                        channels = []
                        lower_subscription_fee =  types.InlineKeyboardButton(text="I want to lower my subscription fee", callback_data="lower_subscription_fee")

                        # Создаем ссылки на счет
                        for channel_name, channel_cost in config["channels"]["channels_cost"].items():
                            user_channel_status = await bot.get_chat_member(chat_id=channel_id, user_id=message.from_user.id)

                            # Если пользователь подписан на канал
                            if user_channel_status.status != 'left':
                                continue

                            channels.append(types.InlineKeyboardButton(text=f"{channel_name} - {config["payment"]["pay_wallet"]}{channel_cost} for {config["payment"]["subscription_duration"]} days",\
                                                                    callback_data=f"{channel_name}"))
                            
                        channels.append(lower_subscription_fee)
                        
                        free_trial_end_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[channels])

                        await bot.send_message(chat_id=user_id, text=message, reply_markup=free_trial_end_keyboard)

                # Если пользователь подписан на канал, но подписки нет
                elif date_channel is None and user_channel_status.status != 'left' and user_channel_status.status != 'kicked' and user_data[1] == 0:
                    try:
                        print(f'Бан пользователя id={user_id}. Пользователь без подписки')
                        await bot.ban_chat_member(channel_id, user_id)
                    except Exception as e:
                        print(f'Не удалось заблокировать пользователя {user_id}\tError={e}')