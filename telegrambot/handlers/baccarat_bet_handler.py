from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes
from Games.models.baccarat_bet import BaccaratBetService
from telegrambot.utils import (
    parse_positive_float,
    get_back_to_casino,
    get_or_create_user,
    back_to_options,
    main_menu_buttons,
    BET_TYPE,
    AMOUNT,
    user_manager
)
from Accounts.models.user import BetType



async def baccarat_bet_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the Baccarat betting process by prompting the user to select a bet option."""
    query = update.callback_query
    await query.answer()

    # Betting options for Baccarat
    buttons = [
        [InlineKeyboardButton(text='🃏 Player', callback_data='player'), InlineKeyboardButton(
            text='🏦 Banker', callback_data='banker')],
        [InlineKeyboardButton(text='🎲 Tie', callback_data='tie')],
        [InlineKeyboardButton(text='❌ Cancel', callback_data='cancel')]
    ]

    await query.edit_message_text(
        text='🎰 *Baccarat Game* 🎰\n\n💰 *Please choose your bet option:*',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return BET_TYPE


async def amount_handler_baccarat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the user’s bet amount input after selecting a bet type."""
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        await back_to_options(update, context, text='🔥 *Fire Casino* 🔥\n\n🌟 Please choose an option:', menu=main_menu_buttons())
        return ConversationHandler.END

    context.user_data['betted_option'] = query.data

    await query.edit_message_text(
        text=f'✅ *Selected:* {query.data.upper()}\n\n💵 *Please enter the bet amount:*'
    )
    return AMOUNT


async def baccarat_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes the bet amount, runs the Baccarat game logic, and returns the results."""
    try:
        amount = parse_positive_float(update.message.text)
    except Exception as e:
        await update.message.reply_text(
            text=f'⚠️ {str(e)}',
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END

    betted_option = context.user_data.get('betted_option')
    user = get_or_create_user(str(update.effective_user.id))

    # Create and process the bet
    try:
        baccarat_bet = BaccaratBetService(amount=amount, owner=user)
        text = baccarat_bet.check_winnings(betted_option)

        # Save the bet result for the user
        user.add_bet(BetType.BACCARAT, baccarat_bet.to_dict())
        user_manager.update_user(user)

        # Send result message
        await update.message.reply_text(
            text=text,
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(
            text=str(e),
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END
