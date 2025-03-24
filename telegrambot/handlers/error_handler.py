from telegram import Update
from telegram.ext import ContextTypes


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify the user."""
    print(f"Update {update} caused error {context.error}")
    if update.message:
        await update.message.reply_text("An error occurred. Please try again later.")
