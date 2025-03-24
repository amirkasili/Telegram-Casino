from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes
from Games.models.roulette_bet import RouletteBetService
from telegrambot.utils import (
    roulette_options,
    back_to_options,
    main_menu_buttons,
    parse_positive_float,
    get_back_to_casino,
    NUMBER_COLOR_SELECTION,
    AMOUNT,
    CONFIRM,
    user_manager
)
from Accounts.models.user import BetType

# Start the roulette bet process by prompting the user to choose a target option


async def roulette_bet_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Send the initial options for the user to choose from
    await query.edit_message_text(
        text='🎉 Please choose your target option: 🎯',
        reply_markup=roulette_options()
    )
    return NUMBER_COLOR_SELECTION


# Handle the user's bet selection and ask for the bet amount
async def roulette_bet_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    # Helper function to process the selected bet and prompt for the amount
    def select_bet_and_ask_for_amount(target_data, target_key):
        context.user_data[target_key] = target_data
        # Determine the type of bet (Odds, Evens, Black, Red)
        if target_data == [i for i in range(1, 37) if i % 2 == 1]:
            bet_type = '⚖️ Odds'  # For odd numbers
        elif target_data == [i for i in range(1, 37) if i % 2 == 0]:
            bet_type = '🔢 Evens'  # For even numbers
        elif target_data == 'black':
            bet_type = '🖤 Black'
        elif target_data == 'red':
            bet_type = '❤️ Red'
        else:
            bet_type = '❓ Unknown'

        # Ask the user for the amount after selecting the bet
        text = f'Selected: {bet_type}\n💰 Please enter the amount:'
        return query.edit_message_text(text=text)

    # Handle various selection options (back to main menu or specific bets)
    if query.data == 'back_to_main_menu':
        await back_to_options(update, context, text='🔥 Fire Casino\n\n🌟 Please choose an option:', menu=main_menu_buttons())
        return ConversationHandler.END

    elif query.data == 'odds':
        # Select odd numbers as the target for betting
        target_numbers = [i for i in range(1, 37) if i % 2 == 1]
        await select_bet_and_ask_for_amount(target_numbers, 'target_numbers')
        return AMOUNT  # Move to the next step (amount entry)

    elif query.data == 'evens':
        # Select even numbers as the target for betting
        target_numbers = [i for i in range(1, 37) if i % 2 == 0]
        await select_bet_and_ask_for_amount(target_numbers, 'target_numbers')
        return AMOUNT  # Move to the next step (amount entry)

    elif query.data == 'black':
        # Select 'black' as the target color for betting
        target_color = 'black'
        await select_bet_and_ask_for_amount(target_color, 'color')
        return AMOUNT  # Move to the next step (amount entry)

    elif query.data == 'red':
        # Select 'red' as the target color for betting
        target_color = 'red'
        await select_bet_and_ask_for_amount(target_color, 'color')
        return AMOUNT  # Move to the next step (amount entry)

    else:
        # In case of an unknown selection, go back to the main menu
        await back_to_options(update, context, text='🔥 Fire Casino\n\n🌟 Please choose an option:', menu=main_menu_buttons())
        return ConversationHandler.END


# Ask the user to confirm the amount and display a summary of the bet
async def get_roulette_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Parse the user's entered amount, ensuring it's a positive float
        context.user_data['amount'] = parse_positive_float(
            update.message.text.strip())
    except Exception as e:
        # If there's an error, notify the user and prompt them again
        await update.message.reply_text(
            text=f'⚠️ {str(e)}',
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END

    # Extract the bet details from the user's selection
    target_numbers = context.user_data.get('target_numbers', None)
    if target_numbers:
        if 2 in target_numbers:
            num_type = '🔢 Evens'
        else:
            num_type = '⚖️ Odds'
    target_color = context.user_data.get('color', None)
    amount = context.user_data['amount']

    # Prepare the confirmation buttons
    buttons = [
        [InlineKeyboardButton(text='✅ Confirm', callback_data='confirm'),
         InlineKeyboardButton(text='❌ Cancel', callback_data='cancel')]
    ]

    # Prepare the summary text for the bet
    text = f"📝 Summary of the bet:\n💰 Amount: {amount}\n"
    if target_color:
        text += f"🎨 Target Color: {target_color}"
        await update.message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return CONFIRM
    if target_numbers:
        text += f"🔢 Target Number: {num_type}"
        await update.message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return CONFIRM


# Confirm the bet and calculate the result
async def roulette_bet_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel':
        # If the user cancels, notify them and end the conversation
        await query.edit_message_text(
            text='❌ Bet canceled',
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END

    # Retrieve the user and the bet details
    user = user_manager.get_user(str(update.effective_user.id))
    target_numbers = context.user_data.get('target_numbers', None)
    target_color = context.user_data.get('color', None)
    amount = context.user_data['amount']
    if not user.wallet.have_enough_balance(amount):
        await query.edit_message_text(
            text="You Don't have enough balannce",
            reply_markup=get_back_to_casino()
        )
        return ConversationHandler.END
        
    # Create a new roulette bet service instance
    roulette_bet = RouletteBetService(
        amount=amount,
        owner=user,
        target_color=target_color,
        target_numbers=target_numbers
    )

    # Perform the roulette spin and check if the user won
    result = roulette_bet.roulette_spin()
    prof = roulette_bet.check_winning(result)

    # Save the bet details for the user
    user.add_bet(BetType.ROULETTE, roulette_bet.to_dict())
    user_manager.update_user(user)

    # Prepare the result summary message
    text = (
        f"📝 Summary of the bet:\n"
        f"💰 Amount: {amount}\n"
        f"🎯 Chosen Color/Number: ___{result[0]}=={result[1]}___\n"
        f"💸 Profit: {prof}\n"
        f"📊 Status: {roulette_bet.bet_status}"
    )

    # Send the final bet result to the user
    await query.edit_message_text(
        text=text,
        reply_markup=get_back_to_casino()
    )
    return ConversationHandler.END
