from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import os

""" internal imports """
from db import Config, DataBaseInterface

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

""" OPEN CONFIG """
file_path = 'data/config.json'
if os.path.exists(file_path):
    config_client = Config(file_path)
else:
    raise Exception(f'File {file_path} not found')

back_keyboard = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text="/exit")]
],resize_keyboard=True)

class Add_channel(StatesGroup):
    set_name = State()
    set_cost = State()
    set_decr = State()
    set_id = State()
    set_img_url = State()
    end = State

@router.message(Command("add_channel"))
async def cmd_help(message: Message, state: FSMContext):
    config = config_client.get()
    
    if message.chat.type == "private":
        user_id = message.from_user.id
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
    await message.answer(text='Enter img url:')
    await state.set_state(Add_channel.set_img_url)
# Обрабатываем картинку
@router.message(Add_channel.set_img_url)
async def cmd_help(message: Message, state: FSMContext):
    await state.update_data(img=message.text)
    await message.answer(text='Enter channel id:')
    await state.set_state(Add_channel.set_id)
# Обрабатываем id
@router.message(Add_channel.set_id)
async def cmd_help(message: Message, state: FSMContext):
    config = config_client.get()
    user_id = message.from_user.id
    channel_data = await state.get_data()

    channel_name = channel_data['name']

    res = db.add_column(channel_name.replace(' ','_'), "TEXT")

    if res:
        if channel_name not in config['channels']['paid']:
            config['channels']['paid'][channel_name] = {}
            
        config['channels']['paid'][channel_name]['id'] = message.text
        config['channels']['paid'][channel_name]['cost'] = channel_data['cost']
        config['channels']['paid'][channel_name]['description'] = channel_data['desr']
        config['channels']['paid'][channel_name]['img'] = channel_data['img']

        config_client.post(config)

        await message.answer("success!")
        await state.clear()
    else:
        await message.reply(text='Error adding channel to database')
        await state.clear()

class Del_channel(StatesGroup):
    set_name = State()


@router.message(Command("del_channel"))
async def cmd_del_channel(message: Message, state: FSMContext):
    config = config_client.get()

    if message.chat.type == "private":

        if message.from_user.id in config['admins']:
            channels = ''
            for name in config['channels']['paid'].keys():
                channels += f'\n{name}'

            await state.set_state(Del_channel.set_name)

            await message.answer(text=f"Enter name channel{channels}")

# Обрабатываем имя
@router.message(Del_channel.set_name)
async def cmd_del_channel_name(message: Message, state: FSMContext):
    config = config_client.get()
    try:
        res = db.del_column(message.text.replace(' ','_'))

        if res:
            del config['channels']['paid'][message.text]
            config_client.post(config)
            await message.answer(text='succes!')
        else:
            await message.reply("Error when deleting from database")

    except Exception as e:
        print(e)
        await message.reply(f"Error del channel. Error: {e}")



class Change_channel_data(StatesGroup):
    set_name = State()
    set_data_name = State()
    set_new_value = State()

@router.message(Command("change_channel_data"))
async def cmd_change_channel_data(message: Message, state: FSMContext):
    config = config_client.get()

    if message.chat.type == "private":

        if message.from_user.id in config['admins']:

            channels = ''
            for name in config['channels']['paid'].keys():
                channels += f'\n{name}'

            await state.set_state(Change_channel_data.set_name)

            await message.answer(text=f"Enter name channel{channels}")


@router.message(Change_channel_data.set_name)
async def cmd_change_channel_data(message: Message, state: FSMContext):
    config = config_client.get()
    await state.update_data(name=message.text)

    data_names = ''
    for name in config['channels']['paid'][message.text].keys():
        data_names += f'\n{name}'

    await message.answer(text=f'Enter data name:\n{data_names}')
    await state.set_state(Change_channel_data.set_data_name)

@router.message(Change_channel_data.set_data_name)
async def cmd_help(message: Message, state: FSMContext):
    await state.update_data(data_name=message.text)
    await message.answer(text='Enter new value:')
    await state.set_state(Change_channel_data.set_new_value)


@router.message(Change_channel_data.set_new_value)
async def cmd_help(message: Message, state: FSMContext):
    try:
        config = config_client.get()
        channel_data = await state.get_data()

        channel_name = channel_data['name']
        data_name = channel_data['data_name']
        new_value = message.text

        config['channels']['paid'][channel_name][data_name] = new_value

        config_client.post(config)

        await message.answer(f'Successfully')

    except Exception as e:
        print(f'Error change channel data(config). Error: {e}')
        await message.answer(f'An error occurred. Error: {e}')



class Add_admin(StatesGroup):
    set_id = State()
    
class Del_admin(StatesGroup):
    set_id = State()


@router.message(Command("del_admin"))
async def cmd_del_channel(message: Message, state: FSMContext):
    config = config_client.get()

    if message.chat.type == "private":

        if message.from_user.id in config['admins']:
            channels = ''
            i = 0
            for name in config['admins']:
                channels += f'\n{i}. {name}'
                i += 1

            await state.set_state(Del_admin.set_id)

            await message.answer(text=f"Enter num user {channels}")

# Обрабатываем имя
@router.message(Del_admin.set_id)
async def cmd_del_channel_name(message: Message, state: FSMContext):
    config = config_client.get()
    try:

        del config['admins'][int(message.text)]
        config_client.post(config)
        await message.answer(text='succes!')

    except Exception as e:
        print(e)
        await message.reply(f"Error del admin. Error: {e}")


@router.message(Command("add_admin"))
async def cmd_del_channel(message: Message, state: FSMContext):
    config = config_client.get()

    if message.chat.type == "private":

        if message.from_user.id in config['admins']:
            channels = ''
            for name in config['admins']:
                channels += f'\n{name}'

            await state.set_state(Add_admin.set_id)

            await message.answer(text=f"Enter user id {channels}")

# Обрабатываем имя
@router.message(Add_admin.set_id)
async def cmd_del_channel_name(message: Message, state: FSMContext):
    config = config_client.get()
    try:

        config['admins'].append(int(message.text))
        config_client.post(config)
        await message.answer(text='succes!')

    except Exception as e:
        print(e)
        await message.reply(f"Error add admin. Error: {e}")