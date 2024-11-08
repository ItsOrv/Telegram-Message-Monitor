import os
import asyncio
import logging
from telethon import TelegramClient
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ClientManager:
    def __init__(self, config, active_clients, api_id, api_hash):
        self.config = config
        self.active_clients = active_clients
        self.api_id = api_id
        self.api_hash = api_hash
        self.config_manager = ConfigManager("clients.json", self.config)

    async def detect_sessions(self):
        """Detects new session files and adds them to the config if not already present."""
        sessions = [f for f in os.listdir('.') if f.endswith('.session') and f != 'bot2.session']
        
        # Find sessions that are not already in config
        new_sessions = [s for s in sessions if s not in self.config.get('clients', [])]
        
        if new_sessions:
            self.config.setdefault('clients', []).extend(new_sessions)
            self.config_manager.save_config(self.config)
            logger.info(f"Detected new sessions: {new_sessions}")
        else:
            logger.info("No new sessions detected.")

    async def start_saved_clients(self):
        """Starts all clients listed in the configuration file."""
        await self.detect_sessions()

        for session_name in self.config.get('clients', []):
            try:
                client = TelegramClient(session_name, self.api_id, self.api_hash)
                await client.start()
                
                if await client.is_user_authorized():
                    self.active_clients[session_name] = client
                    logger.info(f"Started client: {session_name}")
                else:
                    logger.warning(f"Client {session_name} is not authorized. Disconnecting.")
                    await client.disconnect()
                
                await asyncio.sleep(1)  # Introduce a delay for natural behavior

            except Exception as e:
                logger.error(f"Failed to start client {session_name}: {e}")

    async def disconnect_all_clients(self):
        """Disconnects all active clients and clears them from the active clients list."""
        for session_name, client in self.active_clients.items():
            try:
                await client.disconnect()
                logger.info(f"Disconnected client: {session_name}")
            except Exception as e:
                logger.error(f"Error disconnecting client {session_name}: {e}")

        self.active_clients.clear()

    async def toggle_client(self, session: str, event):
        """
        Toggles the active/inactive status of a client account.
        
        Args:
            session (str): Session identifier for the account
            event: Telegram event triggering the toggle
        """
        try:
            if session not in self.config.get('clients', []):
                await event.respond("Account not found in the configuration.")
                return

            if session in self.active_clients:
                # Disable the client
                client = self.active_clients.pop(session)
                await client.disconnect()
                await event.respond(f"Account {session} disabled")
                logger.info(f"Disabled client: {session}")

            else:
                # Enable the client
                client = TelegramClient(session, self.api_id, self.api_hash)
                await client.start()

                if await client.is_user_authorized():
                    self.active_clients[session] = client
                    await event.respond(f"Account {session} enabled")
                    logger.info(f"Enabled client: {session}")
                else:
                    await client.disconnect()
                    await event.respond(f"Account {session} could not be authorized")
                    logger.warning(f"Authorization failed for client: {session}")

            # Save updated configuration
            self.config_manager.save_config()

        except Exception as e:
            logger.error(f"Error toggling client {session}: {e}")
            await event.respond("Error toggling account status")

    async def delete_client(self, session: str, event):
        """
        Permanently deletes a client account and its associated data.
        
        Args:
            session (str): Session identifier for the account to delete
            event: Telegram event triggering the deletion
        """
        try:
            # Disconnect and remove active client if exists
            if session in self.active_clients:
                client = self.active_clients.pop(session)
                await client.disconnect()
                logger.info(f"Disconnected client for deletion: {session}")

            # Remove from configuration and clean up session file
            if session in self.config.get('clients', []):
                self.config['clients'].remove(session)
                self.config_manager.save_config()

                # Delete the session file from disk
                session_file = f"{session}"
                if os.path.exists(session_file):
                    os.remove(session_file)
                    logger.info(f"Deleted session file for client: {session}")

                await event.respond("Account deleted successfully")

            else:
                await event.respond("Account not found in the configuration.")
                logger.warning(f"Attempted to delete non-existent client: {session}")

        except Exception as e:
            logger.error(f"Error deleting client {session}: {e}")
            await event.respond("Error deleting account")
