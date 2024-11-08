from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.types import Channel, Chat
from datetime import datetime
import logging
import asyncio
import json
import os

class SignIn:
    def __init__(self, client_manager):
        """
        کلاس SignIn برای مدیریت فرآیند ورود به حساب تلگرام و افزودن حساب به بات.
        
        :param client_manager: شیء ClientManager برای مدیریت حساب‌ها
        """
        self.client_manager = client_manager
        self.bot = client_manager.bot
        self._conversations = {}
        self.logger = logging.getLogger(__name__)

    async def add_account(self, event):
        """شروع فرآیند افزودن حساب با درخواست شماره تلفن."""
        chat_id = event.chat_id
        try:
            await self.bot.bot.send_message(chat_id, "Please enter your phone number:")
            self._conversations[chat_id] = 'phone_number_handler'
            self.logger.info(f"Requested phone number for chat_id: {chat_id}")
        except Exception as e:
            self.logger.error(f"Error in add_account: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred while adding account. Please try again.")

    async def phone_number_handler(self, event):
        """مدیریت و اعتبارسنجی شماره تلفن کاربر و شروع اتصال به تلگرام."""
        chat_id = event.chat_id
        phone_number = event.message.text.strip()
        try:
            client = TelegramClient(phone_number, API_ID, API_HASH)
            await client.connect()

            if not await client.is_user_authorized():
                await self.bot.bot.send_message(chat_id, "Authorizing...")
                await client.send_code_request(phone_number)
                await self.bot.bot.send_message(chat_id, "Enter the verification code:")
                
                self._conversations[chat_id] = 'code_handler'
                self.bot.handlers['temp_client'] = client
                self.bot.handlers['temp_phone'] = phone_number
            else:
                await self.finalize_client_setup(client, phone_number, chat_id)
        except Exception as e:
            self.logger.error(f"Error in phone_number_handler: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred. Please try again.")
            self.cleanup_temp_handlers(chat_id)

    async def code_handler(self, event):
        """بررسی کد تایید ارسال شده توسط کاربر و ادامه فرآیند ورود."""
        chat_id = event.chat_id
        code = event.message.text.strip()
        client = self.bot.handlers.get('temp_client')
        phone_number = self.bot.handlers.get('temp_phone')

        try:
            await client.sign_in(phone_number, code)
            await self.finalize_client_setup(client, phone_number, chat_id)
        except SessionPasswordNeededError:
            await self.bot.bot.send_message(chat_id, "Enter your 2FA password:")
            self._conversations[chat_id] = 'password_handler'
        except Exception as e:
            self.logger.error(f"Error in code_handler: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred. Please try again.")
            self.cleanup_temp_handlers(chat_id)

    async def password_handler(self, event):
        """مدیریت کلمه عبور دومرحله‌ای در صورت نیاز."""
        chat_id = event.chat_id
        password = event.message.text.strip()
        client = self.bot.handlers.get('temp_client')

        try:
            await client.sign_in(password=password)
            phone_number = self.bot.handlers.get('temp_phone')
            await self.finalize_client_setup(client, phone_number, chat_id)
        except Exception as e:
            self.logger.error(f"Error in password_handler: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred. Please try again.")
            self.cleanup_temp_handlers(chat_id)

    async def finalize_client_setup(self, client, phone_number, chat_id):
        """تکمیل تنظیمات نهایی و ذخیره اطلاعات حساب."""
        try:
            session_name = f"{phone_number}_session"
            client.session.save()
            
            # ذخیره اطلاعات حساب در فایل تنظیمات
            self.bot.config['clients'].append({
                "phone_number": phone_number,
                "session": session_name,
                "groups": [],
                "added_date": datetime.now().isoformat(),
                "disabled": False
            })
            self.bot.config_manager.save_config()

            self.bot.active_clients[session_name] = client
            client.add_event_handler(self.process_message, events.NewMessage())

            await self.bot.bot.send_message(chat_id, f"Account {phone_number} added successfully!")
            self.cleanup_temp_handlers(chat_id)
        except Exception as e:
            self.logger.error(f"Error in finalize_client_setup: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred while finalizing setup.")
            self.cleanup_temp_handlers(chat_id)

    def cleanup_temp_handlers(self, chat_id):
        """پاک‌سازی اطلاعات و هندلرهای موقت پس از اتمام فرآیند."""
        if 'temp_client' in self.bot.handlers:
            del self.bot.handlers['temp_client']
        if 'temp_phone' in self.bot.handlers:
            del self.bot.handlers['temp_phone']
        if chat_id in self._conversations:
            del self._conversations[chat_id]
        self.logger.info("Temporary handlers and data cleared.")
