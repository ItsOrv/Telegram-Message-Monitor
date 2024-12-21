# main.py
import logging
from src.client_manager.client_manager import ClientManager
from src.monitor.monitor import Monitor
from src.handlers.command_handler import CommandHandler
from src.handlers.message_handler import MessageHandler
from src.utils.logger import log_info, log_error
from src.bot import Bot
from src.utils.config import API_ID, API_HASH, BOT_TOKEN, CHANNEL_ID, ADMIN_ID

# تنظیمات لاگینگ برای نمایش پیام‌ها
logging.basicConfig(level=logging.INFO)

def main():
    # راه‌اندازی مدیر کلاینت‌ها
    client_manager = ClientManager()
    log_info("Client Manager initialized")

    # راه‌اندازی مانیتور برای کلمات کلیدی
    keywords = ["urgent", "help"]
    monitor = Monitor(keywords)
    log_info("Monitor initialized with keywords: {}".format(keywords))

    # راه‌اندازی هندلر دستورات
    command_handler = CommandHandler()
    log_info("Command Handler initialized")

    # راه‌اندازی هندلر پیام‌ها
    message_handler = MessageHandler()
    log_info("Message Handler initialized")

    # راه‌اندازی ربات تلگرام
    bot = Bot(client_manager, monitor, command_handler, message_handler, API_ID, API_HASH, BOT_TOKEN)
    log_info("Bot initialized")

    # اجرای ربات
    try:
        bot.run()
    except Exception as e:
        log_error(f"An error occurred: {e}")
        raise e

if __name__ == "__main__":
    main()
