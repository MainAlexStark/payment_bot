from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import Message

from aiogram.fsm.state import StatesGroup, State

from strings.en import strings

from db import UserDataBase
import strings

import json, os



router = Router()

db_client = UserDataBase('DB/users.db')

@router.message(Command("add_channel"))
async def cmd_start(message: Message, state: FSMContext):

    if message.chat.type == "private":

        # Получаем путь к текущему файлу temp.py
        current_path = os.path.abspath(__file__)

        # Формируем путь к файлу config.json
        config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

        # Открываем JSON файл
        with open(config_path) as file:
            config = json.load(file)

        user_id = message.from_user.id

        if user_id in config['admins']:
            await message.answer('Еще не готово')
        else:
            await message.reply("You dont have enough access")