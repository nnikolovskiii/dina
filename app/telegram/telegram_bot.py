# app/telegram/telegram_bot.py
import logging
import os
import io  # Add import for io
from typing import Optional

from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,
)
from telegram.constants import ParseMode
from dotenv import load_dotenv

from app.chat.service import ChatService
from app.dina.feedback_agent.pydantic_agent import Agent

load_dotenv()


class TelegramBot:
    def __init__(self, chat_service: ChatService):
        logging.getLogger("httpx").setLevel(logging.WARNING)

        self.chat_service = chat_service
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.application = ApplicationBuilder().token(self.token).build()
        self.bot = self.application.bot
        from app.task_manager.agent import agent
        self.agent: Optional[Agent] = agent
        self._setup_handlers()

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))

    async def initialize_model(self):
        pass  # Existing code

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! I'm your AI assistant. How can I help you today?")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        user_message = update.message.text
        logging.info(f"Received message from {chat_id}: {user_message}")

        try:
            result = await self.agent.run(user_message)
            # Send result.data as a text file instead of a message
            await self.send_text_file(result.data, chat_id)
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            await self.send_message("Sorry, I encountered an error processing your request.", chat_id)

    async def send_text_file(self, text: str, chat_id: int, filename: str = "response.txt"):
        """Send a text string as a .txt file."""
        try:
            # Create an in-memory bytes buffer
            file_buffer = io.BytesIO(text.encode('utf-8'))
            file_buffer.seek(0)  # Ensure the buffer's pointer is at the start

            # Send the document using the buffer
            await self.bot.send_document(
                chat_id=chat_id,
                document=file_buffer,
                filename=filename
            )
        except Exception as e:
            logging.error(f"Failed to send text file: {e}")
            # Fallback to sending as plain text if file fails
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=None  # Disable Markdown formatting
            )

    async def send_message(self, message: str, chat_id: int):
        """Existing method for sending text messages (unchanged)"""
        try:
            escaped_message = self._escape_markdown(message)
            await self.bot.send_message(
                chat_id=chat_id,
                text=escaped_message,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

    def _escape_markdown(self, text: str) -> str:
        """Existing helper method (unchanged)"""
        escape_chars = '_*[]()~`>#+-=|{}.!'
        return ''.join(['\\' + char if char in escape_chars else char for char in text])


    async def start(self):
        """Start the bot with polling"""
        await self.initialize_model()
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def stop(self):
        """Stop the bot gracefully"""
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
