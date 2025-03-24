from telegram import Update
from telegram.ext import ContextTypes
from telegrambot.utils import (
    main_menu_buttons,
    get_or_create_user,
    back_to_options,
    user_manager,
    START_CAPTION
)
from telegrambot.handlers.account_status_handler import account_status_handler
from telegrambot.handlers.deposit_withdraw_handler import withdraw_start, deposit_start
from telegrambot.handlers.bet_handler import bet_button_handler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command.
    Creates or retrieves the user and displays the main menu.
    """
    get_or_create_user(str(update.effective_user.id))  # Ensure user exists
    name = update.effective_user.first_name  # Get user's first name
    user_manager.save_users()  # Save user data

    # Send welcome message with main menu buttons
    await update.message.reply_text(
        text=START_CAPTION.format(name),
        reply_markup=main_menu_buttons()
    )


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles main menu button clicks.
    Redirects users based on their selection.
    """
    query = update.callback_query
    await query.answer()

    data = query.data  # Get callback data
    print(f"User selected: {data}")  # Debugging output

    menu = main_menu_buttons()

    if data == 'bet':
        await bet_button_handler(update, context)  # Handle bet selection
    elif data == 'account_status':
        await account_status_handler(update, context)  # Show account status
    elif data == 'deposit':
        await deposit_start(update, context)  # Handle deposit process
    elif data == 'withdraw':
        await withdraw_start(update, context)  # Handle withdrawal process
    elif data == 'back_to_main_menu':
        await back_to_options(
            update, 
            context, 
            text='🔥 Fire Casino\n\n🌟 Please choose an option:', 
            menu=menu
        )
