# bot.py
import time
from telethon import TelegramClient, events
from src.utils.logger import log_info
from src.handlers.callback_handler import CallbackHandler
from src.handlers.vars_handler import VarsHandler
from src.handlers.command_handler import CommandHandler
from src.handlers.message_handler import MessageHandler
from src.monitor.monitor import Monitor
from src.client_manager.client_manager import ClientManager
from src.utils.config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_ID

class Bot:
    def __init__(self, client_manager, monitor, command_handler, message_handler, api_id, api_hash, bot_token):
        self.client_manager = client_manager
        self.monitor = monitor
        self.command_handler = command_handler
        self.message_handler = message_handler

        # تنظیمات ربات تلگرام
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.channel_id = CHANNEL_ID
        self.admin_id = ADMIN_ID

        self.client = TelegramClient("bot_session", self.api_id, self.api_hash)

    def start(self):
        """راه‌اندازی ربات و ورود به حساب تلگرام"""
        log_info("Bot is starting...")
        self.client.start(bot_token=self.bot_token)
        log_info("Logged in successfully!")

    def stop(self):
        """متوقف کردن ربات"""
        log_info("Stopping bot...")
        self.client.disconnect()

    def process_message(self, message):
        """پردازش پیام‌ها و ارسال پاسخ‌ها"""
        log_info(f"Received message: {message.text}")

        # بررسی کلمات کلیدی برای مانیتورینگ
        self.monitor.monitor_message(message.text)

        # پردازش دستورات
        self.message_handler.handle_message(message)

    def add_handler(self, handler):
        """اضافه کردن هندلر جدید به ربات"""
        self.client.add_event_handler(handler)

    def run(self):
        """اجرای ربات و دریافت پیام‌ها"""
        self.start()

        # تعریف هندلر پیام
        @self.client.on(events.NewMessage)
        async def on_new_message(event):
            self.process_message(event.message)

        # اجرای ربات
        log_info("Bot is running...")
        self.client.run_until_disconnected()

    def send_message(self, chat_id, text):
        """ارسال پیام به یک چت خاص"""
        self.client.send_message(chat_id, text)
        log_info(f"Message sent to {chat_id}: {text}")
