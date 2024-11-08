import logging
import os
import json
import asyncio
from telethon import events, Button
from telethon.errors import FloodWaitError
from telethon.tl.types import Chat, Channel

logger = logging.getLogger(__name__)

class StatsHandler:
    def __init__(self, bot):
        """
        Initialize StatsHandler with bot instance.
        
        :param bot: Instance of bot to access configuration and active clients.
        """
        self.bot = bot

    async def show_stats(self, event):
        """
        Display statistics of the bot, including total and active accounts, keywords,
        and ignored users.
        
        :param event: Event that triggered the statistics display.
        """
        logger.info("Displaying bot statistics in StatsHandler")
        try:
            stats = {
                "Total Accounts": len(self.bot.config['clients']),
                "Active Accounts": len(self.bot.active_clients),
                "Keywords": len(self.bot.config['KEYWORDS']),
                "Ignored Users": len(self.bot.config['IGNORE_USERS'])
            }

            text = "Bot Statistics\n\n" + "\n".join(f"• {key}: {value}" for key, value in stats.items())
            await event.respond(text)

        except Exception as e:
            logger.error(f"Error displaying stats: {e}")
            await event.respond("Error showing statistics. Please try again.")

    async def update_groups(self, event):
        """
        Update group information for all clients and save them to clients.json.
        
        :param event: Event that triggered the update process.
        """
        logger.info("Updating group information for all clients in StatsHandler")
        try:
            status_message = await event.respond("Please wait, identifying groups for each client...")
            groups_per_client = {}
            json_data = self._initialize_json_data()
            
            for session_name, client in self.bot.active_clients.items():
                group_ids = await self._process_client_groups(client, session_name, status_message)
                if group_ids is not None:
                    groups_per_client[session_name] = group_ids

            # Update JSON data with new groups and save it
            self._save_updated_groups(groups_per_client, json_data)
            await status_message.edit(f"Groups identified and saved successfully for all clients!")
            
        except Exception as e:
            logger.error(f"Error updating groups: {e}")
            await event.respond(f"Error identifying groups: {str(e)}")

    async def show_accounts(self, event):
        """
        Display all registered accounts with status and control options.
        
        :param event: Event that triggered account display.
        """
        logger.info("Displaying registered accounts in StatsHandler")
        try:
            clients_data = self.bot.config.get('clients', {})
            if not isinstance(clients_data, dict) or not clients_data:
                await event.respond("No accounts added yet.")
                return

            messages = [
                self._format_account_message(session, groups)
                for session, groups in clients_data.items()
            ]

            for message_text, message_buttons in messages:
                await event.respond(message_text, buttons=message_buttons)

        except Exception as e:
            logger.error(f"Error displaying accounts: {e}")
            await event.respond("Error showing accounts. Please try again.")

    def _initialize_json_data(self):
        """Initialize JSON data structure for clients.json."""
        json_data = {
            "TARGET_GROUPS": [],
            "KEYWORDS": [],
            "IGNORE_USERS": [],
            "clients": {}
        }

        if os.path.exists("clients.json"):
            try:
                with open("clients.json", "r", encoding='utf-8') as json_file:
                    loaded_data = json.load(json_file)
                    json_data.update(loaded_data)
                    if isinstance(json_data["clients"], list):
                        json_data["clients"] = {session: [] for session in json_data["clients"]}
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON: {e}")

        return json_data

    async def _process_client_groups(self, client, session_name, status_message):
        """Process each client's groups and return a list of group IDs."""
        logger.info(f"Processing groups for client: {session_name}")
        group_ids = set()

        try:
            async for dialog in client.iter_dialogs(limit=None):
                if isinstance(dialog.entity, (Chat, Channel)) and not (isinstance(dialog.entity, Channel) and dialog.entity.broadcast):
                    group_ids.add(dialog.entity.id)

                if len(group_ids) % 50 == 0:
                    await asyncio.sleep(2)  # Rate limiting protection

            await status_message.edit(f"Found {len(group_ids)} groups for {session_name}")
            return list(group_ids)

        except FloodWaitError as e:
            logger.info(f"FloodWaitError: Sleeping for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return None

        except Exception as e:
            logger.error(f"Error in group processing for {session_name}: {e}")
            return None

    def _save_updated_groups(self, groups_per_client, json_data):
        """Save updated group data to clients.json."""
        for session_name, group_ids in groups_per_client.items():
            existing_groups = json_data["clients"].get(session_name, [])
            json_data["clients"][session_name] = list(set(existing_groups + group_ids))

        with open("clients.json", "w", encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            logger.info(f"Saved updated data for {len(groups_per_client)} clients")

    def _format_account_message(self, session, groups):
        """Format account message with buttons for display."""
        phone = session.replace('.session', '') if session else 'Unknown'
        groups_count = len(groups)
        status = "🟢 Active" if session in self.bot.active_clients else "🔴 Inactive"
        
        text = (
            f"• Phone: {phone}\n"
            f"• Groups: {groups_count}\n"
            f"• Status: {status}\n"
        )

        buttons = [
            [
                Button.inline(
                    "❌ Disable" if status == "🟢 Active" else "✅ Enable", 
                    data=f"toggle_{session}"
                ),
                Button.inline("🗑 Delete", data=f"delete_{session}")
            ]
        ]
        return text, buttons
