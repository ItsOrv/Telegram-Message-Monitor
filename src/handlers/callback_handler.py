from telethon import events
from handlers.account_handler import AccountHandler
from handlers.keyword_handler import KeywordHandler
from handlers.stats_handler import StatsHandler
import logging

logger = logging.getLogger(__name__)

class CallbackHandler:
    def __init__(self, bot):
        self.bot = bot

    async def callback_handler(self, event):
        """Handle callback queries"""
        print("callback_handler in CallbackHandler")
        try:
            data = event.data.decode()

            if data == 'add_account':
                print("add_account in callback_handler in CallbackHandler")
                await AccountHandler(self.bot).add_account(event)
            elif data == 'request_phone_number':
                print("request_phone_number in callback_handler in CallbackHandler")
                await event.respond("Please enter your phone number:")
                self.bot._conversations[event.chat_id] = 'phone_number_handler'
            elif data == 'show_accounts':
                print("show_accounts in callback_handler in CallbackHandler")
                await AccountHandler(self.bot).show_accounts(event)
            elif data == 'update_groups':
                print("update_groups in callback_handler in CallbackHandler")
                await AccountHandler(self.bot).update_groups(event)
            elif data.startswith('toggle_'):
                print("toggle_ in callback_handler in CallbackHandler")
                session = data.replace('toggle_', '')
                await AccountHandler(self.bot).toggle_client(session, event)
            elif data.startswith('delete_'):
                print("delete_ in callback_handler in CallbackHandler")
                session = data.replace('delete_', '')
                await AccountHandler(self.bot).delete_client(session, event)
            elif data == 'add_keyword':
                print("add_keyword in callback_handler in CallbackHandler")
                await KeywordHandler(self.bot).add_keyword_handler(event)
            elif data == 'remove_keyword':
                print("remove_keyword in callback_handler in CallbackHandler")
                await KeywordHandler(self.bot).remove_keyword_handler(event)
            elif data == 'show_stats':
                print("show_stats in callback_handler in CallbackHandler")
                await StatsHandler(self.bot).show_stats(event)
            
        except Exception as e:
            logger.error(f"Error in callback_handler: {e}")
            await event.respond("Error processing request. Please try again.")
