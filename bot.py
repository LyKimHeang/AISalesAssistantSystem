import os
import telebot
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the same folder as bot.py
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

# ── Connect to Telegram ────────────────────────────────────────────────────────
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found. Check your .env file.")

bot = telebot.TeleBot(TOKEN)

# Import the same functions used by the website — no duplicate logic
from database import search_product, save_chat_history
from ai import get_ai_response


# ── /start command ─────────────────────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Welcome to the AI Sales Assistant!\n\n"
        "You can ask me anything about our products.\n\n"
        "Example:\n"
        "• Do you have a laptop?\n"
        "• How much is the iPhone 15?\n"
        "• Is the keyboard in stock?"
    )


# ── /help command ──────────────────────────────────────────────────────────────
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
        "🛍️ Just type your question in plain text.\n\n"
        "I'll check our product database and give you an answer instantly."
    )


# ── Handle all regular text messages ──────────────────────────────────────────
@bot.message_handler(func=lambda message: True)
def handle_question(message):

    question = message.text

    # 1. Search database for the product
    product = search_product(question)

    # 2. Get AI-generated response
    ai_response = get_ai_response(question, product)

    # 3. Save to chat history (platform = "telegram" so you can filter later)
    save_chat_history(question, ai_response, platform="telegram")

    # 4. Reply to the user on Telegram
    bot.reply_to(message, ai_response)


# ── Start the bot ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("Bot is running... Press CTRL+C to stop.")
    bot.infinity_polling()