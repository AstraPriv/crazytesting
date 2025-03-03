import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define your Telegram bot token (get this from @BotFather)
TOKEN = "7746986488:AAFaNalzz7p78_rBPl8pscBtVVYIn2xZF24"

# Base URL for your webapp - change this to your actual hosted domain
# For testing, you can use ngrok: e.g., "https://abc123.ngrok.io"
BASE_WEBAPP_URL = "https://your-domain.com"  # Replace with your actual domain

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with buttons that open web apps."""
    # Get user info
    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    
    # Create webapp URL with user parameters
    webapp_url = f"{BASE_WEBAPP_URL}?id={user_id}&username={username}"
    
    # Using WebApp with user params in URL
    keyboard = [
        [
            InlineKeyboardButton(
                "View Solana Wallet", web_app=WebAppInfo(url=webapp_url)
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if image exists
    if os.path.isfile("wallet_start.jpg"):
        # Send the image with caption and buttons
        await update.message.reply_photo(
            photo=open("wallet_start.jpg", "rb"),
            caption="Welcome to your Solana Wallet! Click below to view your wallet:",
            reply_markup=reply_markup
        )
    else:
        # Fallback if image doesn't exist
        await update.message.reply_text(
            "Welcome to your Solana Wallet! Click below to view your wallet:", 
            reply_markup=reply_markup
        )

def main() -> None:
    """Start the bot."""
    # Create the Application with job_queue=None to avoid weakref issues in Python 3.13
    application = Application.builder().token(TOKEN).job_queue(None).build()

    # Register command handler
    application.add_handler(CommandHandler("start", start))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()