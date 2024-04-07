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

class Add_channel(StatesGroup):
    set_name = State()
    set_cost = State()
    set_decr = State()
    set_id = State()
    end = State

@router.message(Command("add_channel"))
async def cmd_help(message: Message, state: FSMContext):
    db_client = UserDataBase('DB/users.db')

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

                await message.answer(text='Enter channel name:')

                await state.set_state(Add_channel.set_name)

# Обрабатываем имя
@router.message(Add_channel.set_name)
async def cmd_help(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Enter channel cost:')
    await state.set_state(Add_channel.set_cost)
# Обрабатываем цену
@router.message(Add_channel.set_cost)
async def cmd_help(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    await message.answer(text='Enter channel description:')
    await state.set_state(Add_channel.set_decr)
# Обрабатываем описание
@router.message(Add_channel.set_decr)
async def cmd_help(message: Message, state: FSMContext):
    await state.update_data(desr=message.text)
    await message.answer(text='Enter channel id:')
    await state.set_state(Add_channel.set_id)
# Обрабатываем id
@router.message(Add_channel.set_id)
async def cmd_help(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db_client = UserDataBase('DB/users.db')
    channel_data = await state.get_data()

    db_client.add_column(channel_data['name'], 'TEXT')

    # Получаем путь к текущему файлу temp.py
    current_path = os.path.abspath(__file__)

    # Формируем путь к файлу config.json
    config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

    # Открываем JSON файл
    with open(config_path, 'r+') as file:
        config = json.load(file)

        config['channels']['channels_cost'][channel_data['name']] = channel_data['cost']
        config['channels']['channels_description'][channel_data['name']] = channel_data['desr']
        config['channels']['channels_id'][channel_data['name']] = message.text

        file.seek(0)  # Перемещаем указатель в начало файла
        json.dump(config, file)
        file.truncate()  # Обрежьте файл, если новые данные занимают меньше места, чем предыдущие

        await message.answer(text=f'Success:\ncost={channel_data['cost']}\ndescription={channel_data['desr']}\nid={message.text}')
        await state.clear()

class Del_channel(StatesGroup):
    set_name = State()

@router.message(Command("del_channel"))
async def cmd_del_channel(message: Message, state: FSMContext):
    db_client = UserDataBase('DB/users.db')

    if message.chat.type == "private":

        await state.set_state(Del_channel.set_name)

        await message.answer(text='Enter name channel')

# Обрабатываем имя
@router.message(Del_channel.set_name)
async def cmd_del_channel_name(message: Message, state: FSMContext):
    db_client = UserDataBase('DB/users.db')

    db_client.del_column(message.text)

    # Получаем путь к текущему файлу temp.py
    current_path = os.path.abspath(__file__)

    # Формируем путь к файлу config.json
    config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

    # Открываем JSON файл
    with open(config_path, 'r+') as file:
        config = json.load(file)

        del config['channels']['channels_cost'][message.text]
        del config['channels']['channels_description'][message.text]
        del config['channels']['channels_id'][message.text]

        file.seek(0)  # Перемещаем указатель в начало файла
        json.dump(config, file)
        file.truncate()  # Обрежьте файл, если новые данные занимают меньше места, чем предыдущие

    await message.answer(text=f'Success: del {message.text}')

    await state.clear()


class Change_payment(StatesGroup):
    set_name = State()
    set_value = State()

@router.message(Command("change_payment_settings"))
async def cmd_del_channel(message: Message, state: FSMContext):
    db_client = UserDataBase('DB/users.db')

    if message.chat.type == "private":

        # Получаем путь к текущему файлу temp.py
        current_path = os.path.abspath(__file__)

        # Формируем путь к файлу config.json
        config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

        # Открываем JSON файл
        with open(config_path, 'r+') as file:
            config = json.load(file)

            await message.answer(text=str(config['payment']))

        await state.set_state(Change_payment.set_name)

        await message.answer(text='Enter key')



@router.message(Change_payment.set_name)
async def cmd_del_channel(message: Message, state: FSMContext):
    db_client = UserDataBase('DB/users.db')
    await state.update_data(name=message.text)

    await message.answer(text='Enter value')
    
    await state.set_state(Change_payment.set_value)


@router.message(Change_payment.set_value)
async def cmd_del_channel(message: Message, state: FSMContext):
    db_client = UserDataBase('DB/users.db')
    data = await state.get_data()

    # Получаем путь к текущему файлу temp.py
    current_path = os.path.abspath(__file__)

    # Формируем путь к файлу config.json
    config_path = os.path.join(os.path.dirname(current_path), '../../config.json')

    with open(config_path, 'r+') as file:
        config = json.load(file)

        config['payment'][data['name']] = int(message.text)

        file.seek(0)  # Перемещаем указатель в начало файла
        json.dump(config, file)
        file.truncate()  # Обрежьте файл, если новые данные занимают меньше места, чем предыдущие

        await message.answer(text='Success')
    
    await state.clear()