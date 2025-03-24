from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes
from telegrambot.utils import (
    get_back_to_casino,
    parse_positive_float,
    limbo_multipliers,
    NUMBER_COLOR_SELECTION,
    AMOUNT,
    CONFIRM,
    user_manager,
    get_or_create_user,
    back_to_options,
    bets_options
)
from Games.models.limbo_bet import LimboBetService
from Accounts.models.user import BetType


async def limbo_bet_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Starts the Limbo bet conversation.
    Displays multiplier options for the user to choose from.
    """
    query = update.callback_query
    await query.answer()

    # Generate buttons for each multiplier
    buttons = [[InlineKeyboardButton(text=f'{multiplier}', callback_data=str(
        multiplier))] for multiplier in limbo_multipliers]
    buttons.append([InlineKeyboardButton(
        text='🔙 Back to bet options', callback_data='back_to_bet_menu')])

    # Send message with available multipliers
    await query.edit_message_text(
        text='🎯 Multipliers\n\nPlease choose your target multiplier:',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return NUMBER_COLOR_SELECTION


async def limbo_bet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's selection of a target multiplier.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'back_to_bet_menu':
        # Go back to bet options menu
        await back_to_options(update, context, text='🎰 Bet Options\n\nPlease choose one:', menu=bets_options())
        return ConversationHandler.END

    # Store selected multiplier
    context.user_data['target_multiplier'] = float(query.data)

    # Ask user to enter bet amount
    await query.edit_message_text(
        text=f'✅ Selected {query.data}\n\n💰 Please enter the bet amount:'
    )
    return AMOUNT


async def bet_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's input of the bet amount.
    """
    try:
        context.user_data['amount'] = parse_positive_float(
            update.message.text.strip())
    except Exception as e:
        await update.message.reply_text(
            text=f'⚠️ {str(e)}',
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END

    target = context.user_data.get('target_multiplier')
    amount = context.user_data.get('amount')

    # Confirmation buttons
    buttons = [
        [InlineKeyboardButton(
            text='✅ Confirm', callback_data='confirm_limbo')],
        [InlineKeyboardButton(text='❌ Cancel', callback_data='cancel')]
    ]

    # Send confirmation message
    await update.message.reply_text(
        text=f"🎲 Placing bet on Limbo with target multiplier of {target}\n💸 Amount: {amount}\n\n🔎 Please confirm the bet:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return CONFIRM


async def confirm_limbo_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the final confirmation of the bet.
    Processes the bet and updates the user's account.
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        # If user cancels, return to casino menu
        await query.edit_message_text(
            text='❌ Bet canceled',
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END

    target = context.user_data.get('target_multiplier')
    amount = context.user_data.get('amount')
    user = get_or_create_user(str(update.effective_user.id))
    if not user.wallet.have_enough_balance(amount):
        await query.edit_message_text(
            text="You Don't have enough balannce",
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END

        # Create and process the Limbo bet
    limbo_bet = LimboBetService(
        amount=amount,
        target_multiplier=target,
        owner=user
    )
    result = limbo_bet.get_multiplier()
    limbo_bet.check_winning(result)
    profit = limbo_bet.bet.calculate_profit()

    # Store bet details in user's history
    user.add_bet(BetType.LIMBO, limbo_bet.to_dict())
    user_manager.update_user(user)

    # Send bet result summary
    text = (
        f"📜 Bet Summary:\n"
        f"🎯 Chosen multiplier:\n\n_________{result}_________\n\n"
        f"📊 Status: {limbo_bet.bet_status}\n"
        f"💰 Amount: {amount}\n"
        f"💵 Profit: {profit}"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_back_to_casino()
    )
    return ConversationHandler.END
