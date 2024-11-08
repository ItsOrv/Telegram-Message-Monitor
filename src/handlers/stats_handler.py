import logging
from telethon import events

logger = logging.getLogger(__name__)

class StatsHandler:
    def __init__(self, bot):
        self.bot = bot


    async def show_stats(self, event):
        """Show bot statistics"""
        logger.info("show_stats in StatsHandler")
        try:
            stats = {
                "Total Accounts": len(self.bot.config['clients']),
                "Active Accounts": len(self.bot.active_clients),
                "Keywords": len(self.bot.config['KEYWORDS']),
                "Ignored Users": len(self.bot.config['IGNORE_USERS'])
            }

            text = "Bot Statistics\n\n"
            for key, value in stats.items():
                text += f"• {key}: {value}\n"

            await event.respond(text)

        except Exception as e:
            logger.error(f"Error showing stats: {e}")
            await event.respond("Error showing statistics")


    async def update_groups(self, event):
        """
        Updates group information for all clients.
        
        Args:
            event: Telegram event triggering the update
            
        # TODO: Implement incremental updates
        # TODO: Add group metadata caching
        # TODO: Implement proper error handling for rate limits
        """
        logger.info("update_groups in AccountHandler")

        groups_per_client = {}
        self.ClientManager.detect_sessions()

        try:
            status_message = await event.respond("Please wait, Identifying groups for each client...")

            # Initialize JSON structure
            json_data = {
                "TARGET_GROUPS": [],
                "KEYWORDS": [],
                "IGNORE_USERS": [],
                "clients": {}
            }
            
            # Load existing data
            if os.path.exists("clients.json"):
                try:
                    with open("clients.json", "r", encoding='utf-8') as json_file:
                        loaded_data = json.loads(json_file.read())
                        json_data.update(loaded_data)
                        if isinstance(json_data["clients"], list):
                            json_data["clients"] = {session: [] for session in json_data["clients"]}
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")

            # Process each client
            for session_name, client in self.bot.active_clients.items():
                try:
                    logger.info(f"Processing client: {session_name}")
                    group_ids = set()

                    try:
                        dialogs = []
                        async for dialog in client.iter_dialogs(limit=None):
                            try:
                                if isinstance(dialog.entity, (Chat, Channel)) and not (
                                    isinstance(dialog.entity, Channel) and dialog.entity.broadcast
                                ):
                                    group_ids.add(dialog.entity.id)
                                    
                                if len(group_ids) % 50 == 0:
                                    await asyncio.sleep(2)  # Rate limiting protection
                                    
                            except Exception as e:
                                logger.error(f"Error processing dialog: {e}")
                                continue
                                
                            if len(group_ids) % 20 == 0:
                                await status_message.edit(f"Found {len(group_ids)} groups for {session_name}...")

                    except FloodWaitError as e:
                        wait_time = e.seconds
                        logger.info(f"FloodWaitError: Sleeping for {wait_time} seconds")
                        await status_message.edit(f"Rate limited. Waiting for {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        continue
                        
                    except Exception as e:
                        logger.error(f"Error in dialog iteration: {e}")
                        await status_message.edit(f"Error processing {session_name}: {str(e)}")
                        continue

                    groups_per_client[session_name] = list(group_ids)
                    logger.info(f"Found {len(group_ids)} groups for {session_name}")
                    await status_message.edit(f"Found {len(group_ids)} groups for {session_name}")
                    await asyncio.sleep(3)

                except Exception as e:
                    logger.error(f"Error processing client {session_name}: {e}")
                    continue

            # Update JSON data
            for session_name, group_ids in groups_per_client.items():
                if session_name in json_data["clients"]:
                    existing_groups = json_data["clients"][session_name]
                    if not isinstance(existing_groups, list):
                        existing_groups = []
                    json_data["clients"][session_name] = list(set(existing_groups + group_ids))
                else:
                    json_data["clients"][session_name] = group_ids

            # Save updated data
            with open("clients.json", "w", encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)
                logger.info(f"Saved data for {len(groups_per_client)} clients")

            await status_message.edit(f"That's it, {len(group_ids)} Groups identified and saved successfully for all clients!")

        except Exception as e:
            logger.error(f"Error in update_groups: {e}")
            await event.respond(f"Error identifying groups: {str(e)}")




    #PASS
    async def show_accounts(self, event):
            """
            Display all registered accounts with their current status and controls.
            
            Args:
                event: Telegram event triggering the account display
                
            Returns:
                None. Sends interactive messages to the chat with account information
                and control buttons.
                
            # TODO: Add pagination for large numbers of accounts
            # TODO: Add sorting options (by status, group count, etc)
            # TODO: Consider caching account status for faster display
            """
            logger.info("show_accounts in AccountHandler")
            try:
                # Get client data with empty dict as fallback
                clients_data = self.bot.config.get('clients', {})
                
                # Validate client data structure
                if not isinstance(clients_data, dict) or not clients_data:
                    await event.respond("No accounts added yet.")
                    return

                messages = []

                # Process each client account
                for session, groups in clients_data.items():
                    # Clean up phone number display
                    phone = session.replace('.session', '') if session else 'Unknown'
                    groups_count = len(groups)
                    status = "🟢 Active" if session in self.bot.active_clients else "🔴 Inactive"

                    # Format account information message
                    text = (
                        f"• Phone: {phone}\n"
                        f"• Groups: {groups_count}\n"
                        f"• Status: {status}\n"
                    )

                    # Create interactive control buttons
                    buttons = [
                        [
                            Button.inline(
                                "❌ Disable" if status == "🟢 Active" else "✅ Enable", 
                                data=f"toggle_{session}"
                            ),
                            Button.inline("🗑 Delete", data=f"delete_{session}")
                        ]
                    ]

                    messages.append((text, buttons))

                # Send each account as a separate message with its controls
                for message_text, message_buttons in messages:
                    await event.respond(message_text, buttons=message_buttons)

            except Exception as e:
                logger.error(f"Error in show_accounts: {e}")
                await event.respond("Error showing accounts. Please try again.")

