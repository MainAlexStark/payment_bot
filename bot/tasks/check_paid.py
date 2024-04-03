from datetime import datetime, timedelta
from strings.en import strings
from keyboards.tasks.free_trial import free_trial_end_keyboard
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