import random
import asyncio
import logging
from telethon import Button, events, functions

class Answer:
    def __init__(self, client, message, logger=None):
        """
        کلاس پاسخ برای ارسال پیام و انجام عملیات‌های مختلف در تلگرام.
        
        :param client: شیء اتصال به تلگرام
        :param message: پیام دریافت‌شده از کاربر
        :param logger: لاگر برای ثبت رویدادها
        """
        self.client = client
        self.message = message
        self.logger = logger or logging.getLogger(__name__)

    async def send_response(self, response):
        """ارسال پاسخ به کاربر."""
        try:
            await self.client.send_message(self.message.chat_id, response)
            self.logger.info(f"Sent response: {response}")
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")

    async def reaction(self):
        """ارسال ری‌اکشن به پیام با انتخاب ایموجی و تعداد دلخواه از طرف کاربر."""
        try:
            # نمایش لیست ایموجی‌های قابل انتخاب به کاربر
            available_emojis = ["👍", "❤️", "😂", "👏", "😮"]
            emoji_buttons = [[Button.inline(emoji, data=f"react_{emoji}")] for emoji in available_emojis]

            await self.client.send_message(
                self.message.chat_id,
                "Please choose a reaction emoji:",
                buttons=emoji_buttons
            )
            self.logger.info("Sent emoji options to user.")

            # انتظار برای انتخاب ایموجی از سوی کاربر
            chosen_emoji = await self._wait_for_event(available_emojis, event_type=events.CallbackQuery)
            if not chosen_emoji:
                return await self.send_response("No emoji selected.")

            # درخواست تعداد ری‌اکشن از کاربر
            await self.send_response(f"You selected: {chosen_emoji}. How many reactions would you like to add? (Max: 5)")
            num_reactions = await self._wait_for_event(max_value=5, event_type=events.NewMessage)
            num_reactions = int(num_reactions) if num_reactions and num_reactions.isdigit() else 1

            # اعمال ری‌اکشن‌ها با تاخیر تصادفی
            for _ in range(num_reactions):
                await self.client.send_reaction(self.message.chat_id, self.message.id, chosen_emoji)
                delay = random.uniform(2, 10)
                await asyncio.sleep(delay)
                self.logger.info(f"Added reaction {chosen_emoji} with delay of {delay:.2f} seconds.")

            await self.send_response(f"{num_reactions} reactions added for {chosen_emoji}.")
        except Exception as e:
            self.logger.error(f"Error in reaction process: {e}")

    async def _wait_for_event(self, valid_values=None, event_type=events.NewMessage, max_value=None):
        """
        انتظار برای یک رویداد مشخص و بازگشت مقدار.
        
        :param valid_values: لیست مقادیر معتبر برای بازگشت
        :param event_type: نوع رویداد برای انتظار
        :param max_value: حداکثر مقدار برای انتظار عددی (در صورت نیاز)
        :return: مقدار انتخاب‌شده یا واردشده توسط کاربر
        """
        try:
            @self.client.on(event_type)
            async def handler(event):
                if event.chat_id == self.message.chat_id:
                    if event_type == events.CallbackQuery:
                        chosen_emoji = event.data.decode("utf-8").replace("react_", "")
                        if valid_values and chosen_emoji in valid_values:
                            await event.answer(f"You selected {chosen_emoji}")
                            await event.delete()
                            return chosen_emoji
                    elif event_type == events.NewMessage:
                        try:
                            user_input = event.raw_text.strip()
                            if max_value and user_input.isdigit() and 1 <= int(user_input) <= max_value:
                                await event.respond(f"Reactions set to {user_input}.")
                                return user_input
                            else:
                                await event.respond(f"Please enter a valid number (1 to {max_value}).")
                        except ValueError:
                            await event.respond("Invalid input. Please enter a number.")
            return await handler.wait_event(timeout=30)
        except asyncio.TimeoutError:
            self.logger.warning(f"No response received from user in time for {event_type}.")
            return None

    async def comment(self, comment_text):
        """ارسال کامنت به پیام مورد نظر."""
        try:
            await self.client.send_message(self.message.chat_id, comment_text, reply_to=self.message.id)
            self.logger.info(f"Commented on message {self.message.id} with text: {comment_text}")
        except Exception as e:
            self.logger.error(f"Error commenting on message: {e}")

    async def block(self, user_id):
        """مسدود کردن کاربر."""
        try:
            await self.client(functions.contacts.BlockRequest(user_id))
            self.logger.info(f"Blocked user with ID: {user_id}")
            await self.send_response(f"User {user_id} has been blocked.")
        except Exception as e:
            self.logger.error(f"Error blocking user {user_id}: {e}")

    async def join(self, group_link):
        """پیوستن به گروه یا کانال تلگرام."""
        try:
            await self.client(functions.messages.ImportChatInviteRequest(group_link))
            self.logger.info(f"Joined group with link: {group_link}")
            await self.send_response("Successfully joined the group.")
        except Exception as e:
            self.logger.error(f"Error joining group with link {group_link}: {e}")

    async def leave(self, group_id):
        """ترک گروه یا کانال تلگرام."""
        try:
            await self.client(functions.channels.LeaveChannelRequest(group_id))
            self.logger.info(f"Left group with ID: {group_id}")
            await self.send_response("Successfully left the group.")
        except Exception as e:
            self.logger.error(f"Error leaving group with ID {group_id}: {e}")
