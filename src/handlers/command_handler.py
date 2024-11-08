# src/handlers/command_handler.py

import logging
from keyboards.keyboard import main_menu_keyboard
from telethon import events

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, bot):
        """
        Initializes the CommandHandler with the bot instance and registers commands.
        
        :param bot: The bot instance to handle Telegram events and messages
        """
        self.bot = bot
        self.commands = {}
        
    async def start_command(self, event):
        """
        Handle /start command and display the main menu keyboard.
        """
        logger.info("Handling /start command in CommandHandler")
        try:
            buttons = main_menu_keyboard()
            await event.respond(
                "Welcome to the Telegram Management Bot.\nPlease choose an option:",
                buttons=buttons
            )
        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            await event.respond("Error showing the main menu. Please try again.")

    async def add_command(self, command, handler):
        """
        Register a new command and its handler.

        :param command: Command string (e.g., "/start")
        :param handler: Callable handler function for the command
        """
        logger.info(f"Registering command: {command}")
        self.commands[command] = handler

    async def handle_command(self, command, *args):
        """
        Execute the command's handler if it exists.

        :param command: Command to handle
        :param args: Arguments to pass to the command's handler
        """
        logger.info(f"Handling command: {command}")
        handler = self.commands.get(command)
        if handler:
            await handler(*args)
        else:
            logger.warning(f"Unknown command: {command}")
            await args[0].respond("Unknown command. Please use /start to see available commands.")
