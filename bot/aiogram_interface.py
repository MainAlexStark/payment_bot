from aiogram import Bot, Dispatcher
import os
from db import Config

""" OPEN CONFIG """
file_path = 'data/config.json'
if os.path.exists(file_path):
    config_client = Config(file_path)
else:
    raise Exception(f'File {file_path} not found')

class AiogramInterface():
    def __init__(self, bot: Bot) -> None:
        self._bot = bot


    async def create_chat_invite_link(self, channel_id: int | str) -> str:
        try:
            result = await self._bot.create_chat_invite_link(channel_id, member_limit=1)
            return result.invite_link
        except Exception as e:
            print(e)
            return ''
        
    async def get_chat_member(self, channel_id: int | str, user_id: int) -> str:
        try:
            result = await self._bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            return result.status
        except Exception as e:
            print(f'Error: {e}. channel={channel_id}, user={user_id}')
            return ''
        
    async def get_sub_channels(self, channels: dict, user_id: int) -> dict:
        sub_channels = {}
        for name, id in channels.items():
            try:
                user_channel_status = self.get_chat_member(id, user_id)
                if user_channel_status != 'left' and user_channel_status != 'kicked':
                    sub_channels[name, id]

            except Exception as e:
                print(f'Error: {e}. channel={id}, user={user_id}')

    
    async def unban_chat_member(self, channel_id: str, user_id: int) -> bool:
        try:
            print(channel_id, user_id)
            return await self._bot.unban_chat_member(channel_id, user_id)
        except Exception as e:
                print(f'Error unban member: {e}. user={user_id}')

    async def ban_chat_member(self, channel_id: str | int, user_id: int) -> bool:
        try:
            print(channel_id, user_id)
            return await self._bot.ban_chat_member(channel_id, user_id)
        except Exception as e:
                print(f'Error ban member: {e}. user={user_id}')


    async def msg_to_admins(self, msg: str):
        config = config_client.get()
        for id in config['admins']: await self._bot.send_message(chat_id=id, text=msg)