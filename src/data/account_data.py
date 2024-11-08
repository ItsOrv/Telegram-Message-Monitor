# src/data/account_data.py

class AccountData:
    def __init__(self):
        self.accounts = {}
        self.bot = bot


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

