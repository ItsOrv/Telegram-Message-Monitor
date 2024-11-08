# src/handlers/message_handler.py

import logging
from telethon import events
from handlers.account_handler import AccountHandler
from handlers.keyword_handler import KeywordHandler

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, bot):
        """
        Initialize MessageHandler with bot instance and specific handlers.
        
        :param bot: Bot instance to handle incoming Telegram messages and conversations.
        """
        self.bot = bot
        self.account_handler = AccountHandler(bot)
        self.keyword_handler = KeywordHandler(bot)
        self.handlers_map = {
            'phone_number_handler': self.account_handler.phone_number_handler,
            'code_handler': self.account_handler.code_handler,
            'password_handler': self.account_handler.password_handler,
            'ignore_user_handler': self.keyword_handler.ignore_user_handler,
            'delete_ignore_user_handler': self.keyword_handler.delete_ignore_user_handler,
            'add_keyword_handler': self.keyword_handler.add_keyword_handler,
            'remove_keyword_handler': self.keyword_handler.remove_keyword_handler
        }

    async def message_handler(self, event):
        """
        Handle incoming messages based on the conversation state.
        
        :param event: Telegram event containing message data.
        :return: True if a specific handler was called, False otherwise.
        """
        logger.info("Processing message in MessageHandler")

        chat_id = event.chat_id
        handler_name = self.bot._conversations.get(chat_id)

        if handler_name and handler_name in self.handlers_map:
            handler = self.handlers_map[handler_name]
            logger.info(f"Invoking handler: {handler_name}")
            await handler(event)
            return True
        else:
            logger.info("No specific conversation state for message.")
            return False
