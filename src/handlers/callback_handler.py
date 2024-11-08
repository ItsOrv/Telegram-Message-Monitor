from telethon import events
from handlers.account_handler import AccountHandler
from handlers.keyword_handler import KeywordHandler
from handlers.stats_handler import StatsHandler
import logging

logger = logging.getLogger(__name__)

class CallbackHandler:
    def __init__(self, bot):
        """
        Initialize CallbackHandler with a reference to the bot.
        
        :param bot: Bot instance to handle events and interactions
        """
        self.bot = bot
        # Define a mapping of callback data to handler methods for better readability
        self.callback_actions = {
            'add_account': self.handle_add_account,
            'request_phone_number': self.handle_request_phone_number,
            'show_accounts': self.handle_show_accounts,
            'update_groups': self.handle_update_groups,
            'add_keyword': self.handle_add_keyword,
            'remove_keyword': self.handle_remove_keyword,
            'ignore_user': self.handle_ignore_user,
            'remove_ignore_user': self.handle_remove_ignore_user,
            'show_stats': self.handle_show_stats
        }

    async def callback_handler(self, event):
        """Handle callback queries based on their data."""
        logger.info("callback_handler in CallbackHandler invoked")
        try:
            data = event.data.decode()
            # Use direct call for fixed actions or route dynamically for prefix-based data
            if data in self.callback_actions:
                await self.callback_actions[data](event)
            elif data.startswith('ignore_'):
                await self.handle_ignore_specific_user(data, event)
            elif data.startswith('toggle_'):
                await self.handle_toggle_client(data, event)
            elif data.startswith('delete_'):
                await self.handle_delete_client(data, event)
            else:
                logger.warning(f"Unhandled callback data: {data}")
                await event.respond("Unhandled action.")
        except Exception as e:
            logger.error(f"Error in callback_handler: {e}")
            await event.respond("Error processing request. Please try again.")

    # Individual handler methods for each action

    async def handle_add_account(self, event):
        """Handle adding a new account."""
        logger.info("Adding account via callback_handler")
        await AccountHandler(self.bot).add_account(event)

    async def handle_request_phone_number(self, event):
        """Request user's phone number."""
        logger.info("Requesting phone number")
        await event.respond("Please enter your phone number:")
        self.bot._conversations[event.chat_id] = 'phone_number_handler'

    async def handle_show_accounts(self, event):
        """Show list of accounts."""
        logger.info("Showing accounts list")
        await AccountHandler(self.bot).show_accounts(event)

    async def handle_update_groups(self, event):
        """Update groups list."""
        logger.info("Updating groups")
        await AccountHandler(self.bot).update_groups(event)

    async def handle_add_keyword(self, event):
        """Add a new keyword."""
        logger.info("Adding keyword")
        await KeywordHandler(self.bot).add_keyword_handler(event)

    async def handle_remove_keyword(self, event):
        """Remove a keyword."""
        logger.info("Removing keyword")
        await KeywordHandler(self.bot).remove_keyword_handler(event)

    async def handle_ignore_user(self, event):
        """Ignore a specific user."""
        logger.info("Ignoring user")
        await KeywordHandler(self.bot).ignore_user_handler(event)

    async def handle_remove_ignore_user(self, event):
        """Remove ignored user."""
        logger.info("Removing ignored user")
        await KeywordHandler(self.bot).delete_ignore_user_handler(event)

    async def handle_show_stats(self, event):
        """Show statistics."""
        logger.info("Showing stats")
        await StatsHandler(self.bot).show_stats(event)

    # Dynamic handlers based on data prefixes

    async def handle_ignore_specific_user(self, data, event):
        """Ignore a specific user based on callback data."""
        logger.info("Ignoring specific user in callback")
        user_id = int(data.split('_')[1])
        await KeywordHandler(self.bot).ignore_user(user_id, event)

    async def handle_toggle_client(self, data, event):
        """Toggle client activation status based on session ID."""
        logger.info("Toggling client status")
        session = data.replace('toggle_', '')
        await AccountHandler(self.bot).toggle_client(session, event)

    async def handle_delete_client(self, data, event):
        """Delete a client based on session ID."""
        logger.info("Deleting client")
        session = data.replace('delete_', '')
        await AccountHandler(self.bot).delete_client(session, event)
