# src/client_manager/sign_in.py

from .client_manager import ClientManager
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import Channel, Chat
from datetime import datetime
from asyncio.log import logger
from config import API_ID, API_HASH, CHANNEL_ID
import logging
from clients.client_manager import ClientManager
from telethon.errors import FloodWaitError
import asyncio
import json
import os

class SignIn:
    def __init__(self, client_manager: ClientManager):
        self.client_manager = client_manager
        self.bot = bot
        self._conversations = {}
        self.ClientManager = bot.client_manager 

    async def add_account(self, event):
        """
        Initiates the account addition process by requesting phone number.
        
        Args:
            event: Telegram event containing chat information
            
        # TODO: Consider adding rate limiting to prevent spam
        # TODO: Add validation for phone number format
        """
        logger.info("add_account in AccountHandler")
        try:
            chat_id = event.chat_id
            await self.bot.bot.send_message(chat_id, "Please enter your phone number:")
            self.bot._conversations[chat_id] = 'phone_number_handler'
        except Exception as e:
            logger.error(f"Error in add_account: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred while adding account. Please try again.")

    async def phone_number_handler(self, event):
        """
        Handles phone number verification and initiates client connection.
        
        Args:
            event: Telegram event containing the phone number
            
        # TODO: Add phone number format validation
        # TODO: Implement retry mechanism for failed connections
        # TODO: Add timeout for authorization process
        """
        logger.info("phone_number_handler in AccountHandler")
        try:
            phone_number = event.message.text.strip()
            chat_id = event.chat_id

            client = TelegramClient(phone_number, API_ID, API_HASH)
            await client.connect()

            if not await client.is_user_authorized():
                await self.bot.bot.send_message(chat_id, "authorizing...")
                await client.send_code_request(phone_number)
                await self.bot.bot.send_message(chat_id, "Enter the verification code:")
                self.bot._conversations[chat_id] = 'code_handler'
                self.bot.handlers['temp_client'] = client
                self.bot.handlers['temp_phone'] = phone_number
            else:
                await self.finalize_client_setup(client, phone_number, chat_id)

        except Exception as e:
            logger.error(f"Error in phone_number_handler: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred. Please try again.")
            del self.bot._conversations[chat_id]

    async def code_handler(self, event):
        """
        Processes verification code and completes authentication.
        
        Args:
            event: Telegram event containing the verification code
            
        # TODO: Add code format validation
        # TODO: Implement retry mechanism for incorrect codes
        # TODO: Add maximum attempts limit
        """
        logger.info("code_handler in AccountHandler")
        try:
            code = event.message.text.strip()
            chat_id = event.chat_id
            client = self.bot.handlers.get('temp_client')
            phone_number = self.bot.handlers.get('temp_phone')

            try:
                await client.sign_in(phone_number, code)
                await self.finalize_client_setup(client, phone_number, chat_id)
            except SessionPasswordNeededError:
                await self.bot.bot.send_message(chat_id, "Enter your 2FA password:")
                self.bot._conversations[chat_id] = 'password_handler'

        except Exception as e:
            logger.error(f"Error in code_handler: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred. Please try again.")
            self.cleanup_temp_handlers()

    async def password_handler(self, event):
        """
        Handles 2FA password verification if required.
        
        Args:
            event: Telegram event containing the 2FA password
            
        # TODO: Implement password attempt limiting
        # TODO: Add secure password handling
        """
        logger.info("password_handler in AccountHandler")
        try:
            password = event.message.text.strip()
            chat_id = event.chat_id
            client = self.bot.handlers.get('temp_client')
            phone_number = self.bot.handlers.get('temp_phone')

            await client.sign_in(password=password)
            await self.finalize_client_setup(client, phone_number, chat_id)

        except Exception as e:
            logger.error(f"Error in password_handler: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred. Please try again.")
            self.cleanup_temp_handlers()

    async def finalize_client_setup(self, client, phone_number, chat_id):
        """
        Completes client setup and saves configuration.
        
        Args:
            client: Authorized TelegramClient instance
            phone_number: User's phone number
            chat_id: Chat ID for response messages
            
        # TODO: Implement backup mechanism for session files
        # TODO: Add configuration validation
        # SECURITY: Consider encrypting sensitive data in config
        """
        logger.info("finalize_client_setup in AccountHandler")
        try:
            session_name = f"{phone_number}_session"
            client.session.save()

            # IMPROVEMENT: Consider using a database instead of JSON for client data
            self.bot.config['clients'].append({
                "phone_number": phone_number,
                "session": session_name,
                "groups": [],
                "added_date": datetime.now().isoformat(),
                "disabled": False
            })
            self.bot.config_manager.save_config()

            self.bot.active_clients[session_name] = client
            client.add_event_handler(
                self.process_message,
                events.NewMessage()
            )

            await self.bot.bot.send_message(chat_id, f"Account {phone_number} added successfully!")
            self.cleanup_temp_handlers()

        except Exception as e:
            logger.error(f"Error in finalize_client_setup: {e}")
            await self.bot.bot.send_message(chat_id, "Error occurred while finalizing setup.")
            self.cleanup_temp_handlers()

    def cleanup_temp_handlers(self):
        """
        Removes temporary handlers and data after setup completion.
        
        # TODO: Add verification for complete cleanup
        # TODO: Implement timeout for cleanup process
        """
        logger.info("cleanup_temp_handlers in AccountHandler")
        if 'temp_client' in self.bot.handlers:
            del self.bot.handlers['temp_client']
        if 'temp_phone' in self.bot.handlers:
            del self.bot.handlers['temp_phone']
