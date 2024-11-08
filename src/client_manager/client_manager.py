import os
from telethon import TelegramClient
import logging
from utils.config_manager import ConfigManager
import asyncio

logger = logging.getLogger(__name__)

class ClientManager:
    def __init__(self, config, active_clients, api_id, api_hash):
        self.config = config
        self.active_clients = active_clients
        self.api_id = api_id
        self.api_hash = api_hash
        self.config_manager = ConfigManager("clients.json", self.config)

    #PASS
    async def detect_sessions(self):
        """Detects session files and adds them to the config if not already present."""
        sessions = []
        for filename in os.listdir('.'):
            if filename.endswith('.session') and filename != 'bot2.session' and filename not in self.config.get('clients', []):
                sessions.append(filename)

        if sessions:
            if 'clients' not in self.config:
                self.config['clients'] = []
            self.config['clients'].extend(sessions)
            self.config_manager.save_config(self.config)
            logger.info(f"Detected sessions: {sessions}")
        else:
            logger.info("No new sessions detected.")

    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    async def start_saved_clients(self):
        """Start all clients listed in the configuration."""
        self.detect_sessions()

        for session_name in self.config.get('clients', []):
            client = TelegramClient(session_name, self.api_id, self.api_hash)
            await client.start()
            if await client.is_user_authorized():
                self.active_clients[session_name] = client
                logger.info(f"Started client: {session_name}")
            else:
                logger.info(f"Client {session_name} is not authorized, skipping.")
                await client.disconnect()
            await asyncio.sleep(1)
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    #PASS
    async def disconnect_all_clients(self):
        """Disconnect all active clients."""
        for client in self.active_clients.values():
            await client.disconnect()
        self.active_clients.clear()


    async def toggle_client(self, session: str, event):
        """
        Toggle the active/inactive status of a client account.
        
        Args:
            session (str): Session identifier for the account
            event: Telegram event triggering the toggle
            
        # TODO: Add status transition validation
        # TODO: Implement graceful disconnection handling
        # TODO: Add automatic reconnection attempts for failed enables
        """
        logger.info("toggle_client in AccountHandler")
        try:
            # Validate session exists
            if session not in self.bot.config['clients']:
                await event.respond("Account not found.")
                return

            currently_active = session in self.bot.active_clients

            if currently_active:
                # Handle client disable
                client = self.bot.active_clients[session]
                await client.disconnect()
                del self.bot.active_clients[session]
                await event.respond(f"Account {session} disabled")
            else:
                # Handle client enable
                client = TelegramClient(session, API_ID, API_HASH)
                await client.start()
                self.bot.active_clients[session] = client
                await event.respond(f"Account {session} enabled")

            # Save updated configuration
            self.bot.config_manager.save_config()

        except Exception as e:
            logger.error(f"Error toggling client {session}: {e}")
            await event.respond("Error toggling account status")

    async def delete_client(self, session: str, event):
        """
        Permanently delete a client account and its associated data.
        
        Args:
            session (str): Session identifier for the account to delete
            event: Telegram event triggering the deletion
            
        # TODO: Add confirmation step before deletion
        # TODO: Implement backup before deletion
        # TODO: Add cleanup verification
        # SECURITY: Ensure secure deletion of sensitive data
        """
        logger.info("delete_client in AccountHandler")
        try:
            # Disconnect and remove active client if exists
            if session in self.bot.active_clients:
                client = self.bot.active_clients[session]
                await client.disconnect()
                del self.bot.active_clients[session]

            # Remove from configuration and clean up session file
            if session in self.bot.config['clients']:
                del self.bot.config['clients'][session]
                self.bot.config_manager.save_config()

                # Clean up session file from disk
                session_file = f"{session}"
                if os.path.exists(session_file):
                    os.remove(session_file)

                await event.respond(f"Account deleted successfully")
            else:
                await event.respond("Account not found.")

        except Exception as e:
            logger.error(f"Error deleting client {session}: {e}")
            await event.respond("Error deleting account")