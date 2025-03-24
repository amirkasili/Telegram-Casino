from telegram import Update
from telegram.ext import ContextTypes
from telegrambot.utils import (
    bets_options,
    back_to_options,
    main_menu_buttons,
)


# Menu text and buttons
TEXT_BET_OPTIONS = "🎲 Bet Options\n\n💡 Please choose one:"
MENU_BETS = bets_options()


async def bet_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the bet menu button click.
    Displays available betting options.
    """
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=TEXT_BET_OPTIONS,
        reply_markup=MENU_BETS
    )


async def bet_menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user selections in the bet menu.
    Redirects users to the chosen bet type.
    """
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_to_main_menu":
        await back_to_options(
            update,
            context,
            text="🔥 Fire Casino\n\n🏆 Please choose an option:",
            menu=main_menu_buttons()
        )
    elif data == 'back_to_bet_menu':
        await back_to_options(
            update,
            context,
            text=TEXT_BET_OPTIONS,
            menu=bets_options()
        )
