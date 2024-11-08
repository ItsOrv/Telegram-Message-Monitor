# src/handlers/command_handler.py

class CommandHandler:
    def __init__(self):
        self.commands = {}


    async def start_command(self, event):
        """Handle /start command"""
        logger.info("start command in CommandHandler")
        try:
            buttons = [
                [Button.inline("Add Account", 'add_account')],
                [Button.inline("Show Accounts", b'show_accounts')],
                [Button.inline("Update Groups", b'update_groups')],
                [
                    Button.inline('Add Keyword', b'add_keyword'),
                    Button.inline('Remove Keyword', b'remove_keyword')
                ],
                [
                    Button.inline('Ignore User', b'ignore_user'),
                    Button.inline('Remove Ignore', b'remove_ignore_user')
                ],
                [Button.inline('Stats', b'show_stats')]
                ]

            await event.respond(
                "Telegram Management Bot\n\n",
                buttons=buttons
            )

        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            await event.respond("Error showing menu. Please try again.")









    async def add_command(self, command, handler):
        self.commands[command] = handler

    async def handle_command(self, command, *args):
        if command in self.commands:
            handler = self.commands[command]
            handler(*args)
        else:
            print("Unknown command")
