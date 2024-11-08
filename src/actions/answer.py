import random
import asyncio
import logging
from telethon import Button

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
        """
        ارسال پاسخ به کاربر.

        :param response: پاسخ برای ارسال به کاربر
        """
        try:
            await self.client.send_message(self.message.chat_id, response)
            self.logger.info(f"Sent response: {response}")
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")

    async def reaction(self):
        """
        ارسال ری‌اکشن به پیام با انتخاب ایموجی و تعداد دلخواه از طرف کاربر.
        ابتدا ایموجی‌های در دسترس را نمایش می‌دهد و سپس تعداد انتخاب‌شده را اعمال می‌کند.
        """
        try:
            # دریافت لیست ایموجی‌های در دسترس برای پیام
            available_emojis = ["👍", "❤️", "😂", "👏", "😮"]
            emoji_buttons = [
                [Button.inline(emoji, data=f"react_{emoji}")]
                for emoji in available_emojis
            ]

            # ارسال دکمه‌های شیشه‌ای به کاربر برای انتخاب ایموجی
            await self.client.send_message(
                self.message.chat_id,
                "Please choose a reaction emoji:",
                buttons=emoji_buttons
            )
            self.logger.info("Sent emoji options to user.")

            # انتظار برای انتخاب کاربر
            chosen_emoji = await self.wait_for_emoji_selection(available_emojis)

            # درخواست تعداد ری‌اکشن از کاربر
            await self.client.send_message(
                self.message.chat_id,
                f"You selected: {chosen_emoji}. How many reactions would you like to add? (Max: 5)"
            )
            num_reactions = await self.get_user_reaction_count(max_reactions=5)
            self.logger.info(f"User chose {num_reactions} reactions for emoji {chosen_emoji}.")

            # اعمال ری‌اکشن‌ها با تاخیر تصادفی
            for _ in range(num_reactions):
                await self.client.send_reaction(self.message.chat_id, self.message.id, chosen_emoji)
                delay = random.uniform(2, 10)
                await asyncio.sleep(delay)
                self.logger.info(f"Added reaction {chosen_emoji} with delay of {delay:.2f} seconds.")

            # نمایش پیام تایید به کاربر
            await self.client.send_message(
                self.message.chat_id,
                f"{num_reactions} reactions added for {chosen_emoji}."
            )

        except Exception as e:
            self.logger.error(f"Error in reaction process: {e}")

    async def wait_for_emoji_selection(self, available_emojis):
        """
        انتظار برای انتخاب ایموجی از سوی کاربر.

        :param available_emojis: لیست ایموجی‌های در دسترس برای انتخاب
        :return: ایموجی انتخاب‌شده توسط کاربر
        """
        try:
            # تعریف یک تابع برای انتظار و واکنش به کلیک کاربر روی دکمه‌های شیشه‌ای
            @self.client.on(events.CallbackQuery)
            async def handler(event):
                if event.data.decode('utf-8').startswith("react_"):
                    chosen_emoji = event.data.decode('utf-8').replace("react_", "")
                    if chosen_emoji in available_emojis:
                        await event.answer(f"You selected {chosen_emoji}")
                        await event.delete()  # حذف دکمه‌ها پس از انتخاب
                        return chosen_emoji
            return await handler.wait_event(timeout=30)  # منتظر انتخاب کاربر (حداکثر 30 ثانیه)

        except asyncio.TimeoutError:
            self.logger.warning("No emoji selected by the user.")
            return None

    async def get_user_reaction_count(self, max_reactions):
        """
        تعداد ری‌اکشن‌های درخواستی را از کاربر دریافت می‌کند و آن را محدود به مقدار max_reactions می‌کند.
        
        :param max_reactions: حداکثر تعداد ری‌اکشن‌ها
        :return: تعداد انتخاب‌شده توسط کاربر
        """
        try:
            @self.client.on(events.NewMessage)
            async def handler(event):
                if event.chat_id == self.message.chat_id:
                    try:
                        count = int(event.raw_text)
                        if 1 <= count <= max_reactions:
                            await event.respond(f"Reactions set to {count}.")
                            return count
                        else:
                            await event.respond(f"Please enter a number between 1 and {max_reactions}.")
                    except ValueError:
                        await event.respond("Invalid input. Please enter a number.")
            return await handler.wait_event(timeout=30)

        except asyncio.TimeoutError:
            self.logger.warning("User did not specify the number of reactions.")
            return 1  # مقدار پیش‌فرض در صورت عدم پاسخ کاربر


    async def send_response(self, response):
        """
        ارسال پاسخ به کاربر.

        :param response: پاسخ برای ارسال به کاربر
        """
        try:
            await self.client.send_message(self.message.chat_id, response)
            self.logger.info(f"Sent response: {response}")
        except Exception as e:
            self.logger.error(f"Error sending response: {e}")

    async def reaction(self):
        """
        ارسال ری‌اکشن به پیام با انتخاب ایموجی و تعداد دلخواه از طرف کاربر.
        """
        # پیاده‌سازی فانکشن reaction از کد قبلی استفاده می‌شود
        pass

    async def comment(self, comment_text):
        """
        ارسال کامنت به پیام مورد نظر.

        :param comment_text: متن کامنت برای ارسال
        """
        try:
            # ارسال کامنت به پیام فعلی
            await self.client.send_message(self.message.chat_id, comment_text, reply_to=self.message.id)
            self.logger.info(f"Commented on message {self.message.id} with text: {comment_text}")

        except Exception as e:
            self.logger.error(f"Error commenting on message: {e}")

    async def block(self, user_id):
        """
        مسدود کردن کاربر.

        :param user_id: شناسه کاربر برای مسدود کردن
        """
        try:
            await self.client(functions.contacts.BlockRequest(user_id))
            self.logger.info(f"Blocked user with ID: {user_id}")
            await self.send_response(f"User {user_id} has been blocked.")
        except Exception as e:
            self.logger.error(f"Error blocking user {user_id}: {e}")

    async def join(self, group_link):
        """
        پیوستن به گروه یا کانال تلگرام.

        :param group_link: لینک دعوت به گروه یا کانال
        """
        try:
            await self.client(functions.messages.ImportChatInviteRequest(group_link))
            self.logger.info(f"Joined group with link: {group_link}")
            await self.send_response("Successfully joined the group.")
        except Exception as e:
            self.logger.error(f"Error joining group with link {group_link}: {e}")

    async def left(self, group_id):
        """
        ترک گروه یا کانال تلگرام.

        :param group_id: شناسه گروه یا کانال برای ترک
        """
        try:
            await self.client(functions.channels.LeaveChannelRequest(group_id))
            self.logger.info(f"Left group with ID: {group_id}")
            await self.send_response("Successfully left the group.")
        except Exception as e:
            self.logger.error(f"Error leaving group with ID {group_id}: {e}")
