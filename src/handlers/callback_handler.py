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
        try:
            data = event.data.decode()

            if data == 'add_account':
                await AccountHandler(self.bot).add_account(event)
            elif data == 'show_accounts':
                await AccountHandler(self.bot).show_accounts(event)
            elif data == 'update_groups':
                await AccountHandler(self.bot).update_groups(event)
            elif data.startswith('toggle_'):
                session = data.replace('toggle_', '')
                await AccountHandler(self.bot).toggle_client(session, event)
            elif data.startswith('delete_'):
                session = data.replace('delete_', '')
                await AccountHandler(self.bot).delete_client(session, event)
            elif data == 'add_keyword':
                await KeywordHandler(self.bot).add_keyword_handler(event)
            elif data == 'remove_keyword':
                await KeywordHandler(self.bot).remove_keyword_handler(event)
            elif data == 'show_stats':
                await StatsHandler(self.bot).show_stats(event)
            # Add other callback handlers here if needed

        except Exception as e:
            logger.error(f"Error in callback_handler: {e}")
            await event.respond("Error processing request. Please try again.")
