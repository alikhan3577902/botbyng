from pyrogram.client import Client
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

class TelegramClientManager:
    def __init__(self, session_string: str, api_id: int, api_hash: str):
        self.session_string = session_string
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None
        self.is_running = False

    async def start(self):
        """Initialize and start the Telegram client"""
        try:
            self.client = Client(
                "telegram_session",
                api_id=self.api_id,
                api_hash=self.api_hash,
                session_string=self.session_string
            )
            
            await self.client.start()
            self.is_running = True
            
            # Get current user info to verify session
            me = await self.client.get_me()
            logger.info(f"Successfully logged in as: {me.first_name} ({me.phone_number})")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram client: {e}")
            raise

    async def stop(self):
        """Stop the Telegram client"""
        if self.client and self.is_running:
            await self.client.stop()
            self.is_running = False
            logger.info("Telegram client stopped")

    def get_client(self):
        """Get the Telegram client instance"""
        if not self.client or not self.is_running:
            raise Exception("Telegram client is not running")
        return self.client

    async def send_message(self, chat_id, text):
        """Send a message to a chat"""
        try:
            client = self.get_client()
            return await client.send_message(chat_id, text)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def get_messages(self, chat_id, limit=5):
        """Get recent messages from a chat"""
        try:
            client = self.get_client()
            messages = []
            async for message in client.get_chat_history(chat_id, limit=limit):
                messages.append(message)
            return messages
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            raise

    async def click_inline_button(self, message, button_text):
        """Click an inline keyboard button"""
        try:
            client = self.get_client()
            
            if not message.reply_markup or not message.reply_markup.inline_keyboard:
                raise Exception("Message has no inline keyboard")
            
            # Find the button with matching text
            for row in message.reply_markup.inline_keyboard:
                for button in row:
                    if button.text == button_text:
                        await message.click(button_text)
                        return True
            
            raise Exception(f"Button '{button_text}' not found")
        except Exception as e:
            logger.error(f"Failed to click button: {e}")
            raise
