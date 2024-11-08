# src/monitor/monitor.py

class Monitor:
    def __init__(self, keywords):
        self.keywords = keywords

    async def process_messages_for_client(self, client):
        """
        Sets up message processing for a specific client.
        
        Args:
            client: TelegramClient instance to process messages for
            
        # TODO: Implement message queuing system
        # TODO: Add message deduplication
        # TODO: Implement message filtering optimization
        """
        @client.on(events.NewMessage)
        async def process_message(event):
            """
            Processes and forwards new messages based on configured filters.
            
            Args:
                event: NewMessage event from Telegram
            """
            try:
                message = event.message.text
                if not message:
                    return

                sender = await event.get_sender()
                if not sender or sender.id in self.bot.config['IGNORE_USERS']:
                    return

                if not any(keyword.lower() in message.lower() for keyword in self.bot.config['KEYWORDS']):
                    return

                chat = await event.get_chat()
                chat_title = getattr(chat, 'title', 'Unknown Chat')

                # Format message for forwarding
                text = (
                    f"• User: {getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '')}\n"
                    f"• User ID: `{sender.id}`\n"
                    f"• Chat: {chat_title}\n\n"
                    f"• Message:\n{message}\n"
                )

                # Generate message link
                if hasattr(chat, 'username') and chat.username:
                    message_link = f"https://t.me/{chat.username}/{event.id}"
                else:
                    chat_id = str(event.chat_id).replace('-100', '', 1)
                    message_link = f"https://t.me/c/{chat_id}/{event.id}"

                buttons = [
                    [Button.url("View Message", url=message_link)],
                    [Button.inline("🚫Ignore🚫", data=f"ignore_{sender.id}")]
                ]

                await self.bot.bot.send_message(
                    CHANNEL_ID,
                    text,
                    buttons=buttons,
                    link_preview=False
                )

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

