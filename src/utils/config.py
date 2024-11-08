# config.py
from dotenv import load_dotenv
import os

# بارگذاری مقادیر از فایل .env
load_dotenv()

# دریافت مقادیر از محیط
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

# چاپ مقادیر برای اطمینان از بارگذاری درست
print(f"API_ID: {API_ID}")
print(f"API_HASH: {API_HASH}")
print(f"BOT_TOKEN: {BOT_TOKEN}")
print(f"CHANNEL_ID: {CHANNEL_ID}")
print(f"ADMIN_ID: {ADMIN_ID}")
