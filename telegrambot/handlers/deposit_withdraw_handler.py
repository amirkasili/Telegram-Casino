from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegrambot.utils import (
    get_back_to_casino,
    get_or_create_user,
    parse_positive_float,
    DEPOSIT_AMOUNT,
    WITHDRAW_AMOUNT,
    user_manager
)
import logging

logger = logging.getLogger(__name__)


async def deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit request."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text="💰 Enter the deposit amount ($):",
    )
    return DEPOSIT_AMOUNT


async def deposit_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle deposit amount."""
    user_id = str(update.effective_user.id)
    user = get_or_create_user(user_id)

    try:
        amount = parse_positive_float(update.message.text)
        logger.info(f"Depositing {amount} for user {user_id}.")
        user.wallet.deposit(amount)

        # Save the updated user data
        user_manager.save_users()

        await update.message.reply_text(
            text=f"💸 Successfully deposited {amount:.2f}.\n💶 Your new balance is {user.wallet.balance:.2f}$.",
            reply_markup=get_back_to_casino()
        )
    except Exception as e:
        logger.error(f"Error in deposit_amount_handler: {e}")
        await update.message.reply_text(
            text=str(e),
            reply_markup=get_back_to_casino()
        )
    return ConversationHandler.END


async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdraw request."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text="💲 Enter the withdraw amount ($):",
    )
    return WITHDRAW_AMOUNT


async def withdraw_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdraw amount."""
    user_id = str(update.effective_user.id)
    user = get_or_create_user(user_id)

    try:
        amount = parse_positive_float(update.message.text)
        logger.info(f"Withdrawing {amount} for user {user_id}.")
        user.wallet.withdraw(amount)

        # Save the updated user data
        user_manager.save_users()

        await update.message.reply_text(
            text=f"🤑 Successfully withdrew {amount:.2f}.\n💷Your new balance is {user.wallet.balance:.2f}$.",
            reply_markup=get_back_to_casino()
        )
    except ValueError as e:
        logger.error(f"Error in withdraw_amount_handler: {e}")
        await update.message.reply_text(
            text=str(e),
            reply_markup=get_back_to_casino()
        )
    return ConversationHandler.END
