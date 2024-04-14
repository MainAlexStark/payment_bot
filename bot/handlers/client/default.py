""" third party imports """
import os

from aiogram import Router, F, types
from aiogram.filters import Command, CommandObject, CommandStart

from aiogram import Bot, Dispatcher

from datetime import datetime, timedelta

import re

""" internal imports """
from db import Config, DataBaseInterface
from aiogram_interface import AiogramInterface

router = Router()

""" OPEN DataBase """
file_path = 'data/DataBase.db'
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

async def get_channels_keyboard(bot: Bot, user_id: int, sub: bool) -> types.InlineKeyboardMarkup:
    config = config_client.get()
    ai = AiogramInterface(bot)
    buttons = []

    for name, data in config['channels']['free'].items():
        url = data['url']

        buttons.append([types.InlineKeyboardButton(text=f'Free channel / {name}', url=url)])    

    for name, data in config['channels']['paid'].items():
        id = data['id']
        subscription_duration = int(config['payment']['subscription_duration'])
        trial_period = int(config['payment']['free_trial'])

        link = await ai.create_chat_invite_link(id)

        if len(link) > 0:
            is_sub = db.get_column(user_id=user_id, column=name.replace(' ','_'))
            is_trial = db.get_column(user_id=user_id, column="start_date")

            # If paid channel
            if is_sub is not None:
                date = db.get_column(user_id=user_id, column=name.replace(' ','_'))
                date = datetime.strptime(date, "%d.%m.%Y")
                date_plus_subscription_duration = date + timedelta(days=subscription_duration)
                diff = date_plus_subscription_duration - datetime.now()
                date_plus_subscription_duration = date_plus_subscription_duration.strftime("%d.%m.%Y")
                diff_days = str(diff.days)
                buttons.append([types.InlineKeyboardButton(text=f'{diff_days} days sub / {name} ({date_plus_subscription_duration})', url=link)])
            # If trai period
            elif is_trial is not None:
                date = db.get_column(user_id=user_id, column="start_date")
                date = datetime.strptime(date, "%d.%m.%Y")
                date_plus_subscription_duration = date + timedelta(days=trial_period)
                diff = date_plus_subscription_duration - datetime.now()
                date_plus_subscription_duration = date_plus_subscription_duration.strftime("%d.%m.%Y")
                diff_days = str(diff.days)
                buttons.append([types.InlineKeyboardButton(text=f'{diff_days} days trial / {name} ({date_plus_subscription_duration})', url=link)])
            else:
                if not sub:
                    cost = data['cost']

                    num_purchases = db.get_column(user_id=user_id, column='num_purchases')
                    if num_purchases is not None:
                        num_refferals = db.get_column(user_id=user_id, column='ref_num')
                        if num_refferals is not None:
                            if num_refferals>5:num_refferals=5
                            for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))

                    buttons.append([types.InlineKeyboardButton(text=f"{name} - ${round(cost,2)} for {subscription_duration} days",
                                                        callback_data=f"pay=name")])
        else:
            raise Exception('Error create invite link')
        
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)  

async def get_not_sub_channels_keyboard(bot: Bot, user_id: int):
    config = config_client.get()
    ai = AiogramInterface(bot)
    buttons = []

    for name, data in config['channels']['free'].items():
        url = data['url']

        buttons.append([types.InlineKeyboardButton(text=f"Free channel / {name}", url=url)])    

    all_cost = 0
    for name, data in config['channels']['paid'].items():
        id = data['id'] 
        subscription_duration = config['payment']['subscription_duration']

        is_sub = db.get_column(user_id=user_id, column=name.replace(' ','_'))
        if is_sub is not None:
            continue
        else:
            all_cost += float(data['cost'])
            cost = float(data['cost'])
            num_purchases = db.get_column(user_id=user_id, column='num_purchases')
            if num_purchases is not None:
                num_refferals = db.get_column(user_id=user_id, column='ref_num')
                if num_refferals is not None:
                    if num_refferals>5:num_refferals=5
                    for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))

            buttons.append([types.InlineKeyboardButton(text=f"{name} - ${round(cost,2)} for {subscription_duration} days",
                                                       callback_data=f"pay={name}")])
    if all_cost != 0:
        buttons.append([types.InlineKeyboardButton(text=f"All channels - {round(all_cost,2)} for {subscription_duration} days",callback_data="pay=all")])
            
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)  


async def get_sub_channels_keyboard(bot: Bot, user_id: int):
    config = config_client.get()
    ai = AiogramInterface(bot)
    buttons = []

    for name, data in config['channels']['paid'].items():
        id = data['id']
        subscription_duration = int(config['payment']['subscription_duration'])
        trial_period = int(config['payment']['free_trial'])

        link = await ai.create_chat_invite_link(id)

        if len(link) > 0:
            is_sub = db.get_column(user_id=user_id, column=name.replace(' ','_'))
            is_trial = db.get_column(user_id=user_id, column="start_date")

            # If paid channel
            if is_sub is not None:
                date = db.get_column(user_id=user_id, column=name.replace(' ','_'))
                date = datetime.strptime(date, "%d.%m.%Y")
                date_plus_subscription_duration = date + timedelta(days=subscription_duration)
                diff = date_plus_subscription_duration - datetime.now()
                date_plus_subscription_duration = date_plus_subscription_duration.strftime("%d.%m.%Y")
                diff_days = str(diff.days)
                buttons.append([types.InlineKeyboardButton(text=f'{diff_days} days sub / {name} ({date_plus_subscription_duration})', url=link)])
            # If trai period
            elif is_trial is not None:
                date = db.get_column(user_id=user_id, column="start_date")
                date = datetime.strptime(date, "%d.%m.%Y")
                date_plus_subscription_duration = date + timedelta(days=trial_period)
                diff = date_plus_subscription_duration - datetime.now()
                date_plus_subscription_duration = date_plus_subscription_duration.strftime("%d.%m.%Y")
                diff_days = str(diff.days)
                buttons.append([types.InlineKeyboardButton(text=f'{diff_days} days trial / {name} ({date_plus_subscription_duration})', url=link)])
            

    return types.InlineKeyboardMarkup(inline_keyboard=buttons) 


async def get_all_paid_keyboard(bot: Bot, user_id: int):
    config = config_client.get()
    ai = AiogramInterface(bot)
    buttons = []
    all_cost = 0
    for name, data in config['channels']['paid'].items():
        id = data['id']
        cost = float(data['cost'])
        all_cost += float(cost)
        subscription_duration = int(config['payment']['subscription_duration'])
        trial_period = int(config['payment']['free_trial'])

        num_purchases = db.get_column(user_id=user_id, column='num_purchases')
        if num_purchases is not None:
            num_refferals = db.get_column(user_id=user_id, column='ref_num')
            if num_refferals is not None:
                if num_refferals>5:num_refferals=5
                for i in range(num_refferals):cost = float(cost)*(1-(float(config['payment']['discount'])/100))

        buttons.append([types.InlineKeyboardButton(text=f"{name} - ${round(cost,2)} for {subscription_duration} days",
                                                       callback_data=f"pay={name}")])
            
    num_purchases = db.get_column(user_id=user_id, column='num_purchases')
    if num_purchases is not None:
        num_refferals = db.get_column(user_id=user_id, column='ref_num')
        if num_refferals is not None:
            if num_refferals>5:num_refferals=5
            for i in range(num_refferals):all_cost = float(all_cost)*(1-(float(config['payment']['discount'])/100))

    if all_cost != 0:
        buttons.append([types.InlineKeyboardButton(text=f"All channels - {round(all_cost,2)} fot {subscription_duration} days",callback_data="pay=all")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)    

greet_kb = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text="/active_subscriptions")],
    [types.KeyboardButton(text='/our_offerings'), types.KeyboardButton(text="/referral_system")]
],resize_keyboard=True)


@router.message(Command("start"))
@router.message(Command("our_offerings"))
@router.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'refid_(\d+)'))
    ))
async def cmd_start(message: types.Message, command: CommandObject):
    config = config_client.get()
    # Private chat check 
    if message.chat.type == "private":
        # Get user id
        user_id = message.from_user.id

        if db.is_user(user_id=user_id):
            b = await get_all_paid_keyboard(message.bot, user_id)
            await message.answer(text=strings['handlers']['start'],reply_markup=b, disable_web_page_preview=True)
            await message.answer(text=strings['Terms_of_Service'],reply_markup=greet_kb,parse_mode="HTML", disable_web_page_preview=True)
        # If the user is new
        else:
            if db.add_user(user_id=user_id):

                if command.args:
                    refid = command.args.split("_")[1]
                    if db.change_data(user_id=user_id, column='ref_id', new_value=int(refid)):
                        await message.answer(f"Referral link activated")
                    else:
                        await message.answer(f"Error: Referral link not activated")

                try:
                    channels_keyboard = await get_channels_keyboard(message.bot, user_id=user_id, sub=False)
                    await message.answer(text=strings['handlers']['new_user_start'], reply_markup=channels_keyboard, disable_web_page_preview=True)
                    await message.answer(text=strings['Terms_of_Service'],reply_markup=greet_kb,parse_mode="HTML", disable_web_page_preview=True)
                except Exception as e:
                    print(e)
                    await message.answer(text="An error occurred, please try later")

            else:
                await message.answer(text="An error occurred, please try later")


        if user_id in config['admins']:
            string =''
            for command in config['commands']['admin']:
                string += f"\n/{command}"

            await message.answer(string)


# @router.message(Command("our_products"))
# async def cmd_our_products(message: types.Message):
#     config = config_client.get()
#     # Private chat check 
#     if message.chat.type == "private":
#         # Get user id
#         user_id = message.from_user.id
#         channels_keyboard = await get_channels_keyboard(message.bot, user_id=user_id, sub=False)
#         await message.answer(text="Our Projects:",reply_markup=channels_keyboard)

@router.message(Command("active_subscriptions"))
async def cmd_my_subscriptions(message: types.Message):
    config = config_client.get()
    # Private chat check 
    if message.chat.type == "private":
        user_id = message.from_user.id
        channels_keyboard = await get_sub_channels_keyboard(message.bot, user_id=user_id)
        await message.answer(text="Your subscriptions:",reply_markup=channels_keyboard)


@router.message(Command("referral_system"))
async def cmd_referral_system(message: types.Message):
    config = config_client.get()
    user_id = message.from_user.id
    # Private chat check 
    if message.chat.type == "private":

        if db.get_column(user_id=user_id, column='num_purchases') is not None:

            link = 'https://t.me/Alex_Stark_bot?start=refid_'

            user_id = message.from_user.id
            user_num_referals = 0
            ref_num = db.get_column(user_id=user_id,column="ref_num") 
            if ref_num is not None:
                user_num_referals = ref_num

            msg = f"We`re delighted to have you in our small commodity club. We prioritise relationships and offer you the opportunity to invite five trusted professionals.\n\
An invitation entitles the recipient to a {config['payment']['discount']}% lifetime subscription discount. Also, as long as your invitees are members of our club, you will receive a 20% discount on your subscription for each of them!\n\
Use the link below to extend an invitation: <code>{link}{user_id}</code>\n\
Accepted invitations: {user_num_referals}\n\
Your total discount: [Х]%"
            await message.reply(text=msg, parse_mode="HTML")

        else:
            await message.reply(text="Make your first purchase first!")