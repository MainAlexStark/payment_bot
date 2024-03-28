from aiogram import types
import json, os

# Получаем путь к текущему файлу temp.py
current_path = os.path.abspath(__file__)

# Формируем путь к файлу config.json
config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

# Открываем JSON файл
with open(config_path) as file:
    config = json.load(file)

    channels = []
    lower_subscription_fee =  types.InlineKeyboardButton(text="I want to lower my subscription fee", callback_data="lower_subscription_fee")

    # Создаем ссылки на счет
    for channel_name, channel_cost in config["channels_cost"].items():
        channels.append(types.InlineKeyboardButton(text=f"{channel_name} - {config["pay_wallet"]}{channel_cost} for {config["subscription_duration"]} days",\
                                                  callback_data=f"{channel_name}"))
    channels.append(lower_subscription_fee)
    
    free_trial_end_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[channels])