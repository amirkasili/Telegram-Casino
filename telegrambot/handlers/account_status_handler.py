from telegram import Update
from telegram.ext import ContextTypes
from telegrambot.utils import get_or_create_user, get_back_to_casino, format_bets_history


async def account_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle account status request."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)
    user = get_or_create_user(user_id)

    bets = user.load_bets()

    bet_history = await format_bets_history(user)
    await query.edit_message_text(
        text=f"💰 Your current balance is: {user.wallet.balance:.2f}\n💈 Total bets : {len(bets)}\n\n📜 Bet History:\n{bet_history}",
        reply_markup=get_back_to_casino()
    )
