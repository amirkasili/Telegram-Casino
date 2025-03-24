from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from Accounts.models.user import UserManager, User
from telegram.ext import ContextTypes


# the start caption to show the user
START_CAPTION = """
👋 Hello {} 
🔥 Welcome to the FireBet Demo casino 

🌟Available bets:

🔴roulette - demo roulette 
🎰Baccarat - light baccarat
🚀limbo - love this 

I bet on your win 😉
"""


BET_TYPE, PLACING_BET, AMOUNT_TYPING, AMOUNT, CONFIRM, DEPOSIT_AMOUNT, WITHDRAW_AMOUNT, NUMBER_COLOR_SELECTION, CUSTOM_NUMBER = range(
    9)

limbo_multipliers = [1.3, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 10.0]

user_manager = UserManager()


def main_menu_buttons():
    """return the main menu buttons"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👑Bet", callback_data='bet')],
        [InlineKeyboardButton(
            '💲Account status', callback_data='account_status')],
        [InlineKeyboardButton('🤑Deposit', callback_data='deposit'),
         InlineKeyboardButton("💶Withdraw", callback_data='withdraw')]
    ])


async def back_to_options(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, menu):
    """back to the given menu option"""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=text,
        reply_markup=menu
    )


# return the back to menu button
def get_back_to_casino():
    """return the back to menu button"""
    return InlineKeyboardMarkup([[InlineKeyboardButton('💈 Back To Casino 💈', callback_data='back_to_main_menu')]])


def get_or_create_user(user_id: str):
    """get or create the user"""
    try:
        user_manager.load_users()
    except Exception as e:
        print(f"Error loading users: {e}")
        return None  # or handle appropriately
    user = user_manager.get_user(user_id=user_id)
    if not user:
        user = user_manager.create_user(user_id=user_id)

    return user


def parse_positive_float(text: str) -> float:
    """parse the text to operational float object"""
    num = float(text)
    if num <= 0:
        raise ValueError("Value must be greater than 0")
    return num


async def format_bets_history(user: User):
    bets = user.load_bets()
    bet_history = []
    for bet in bets:
        if bet['type'] == 'ROULETTE':
            if 2 in bet['number']:
                num_type = 'Evens'
            else:
                num_type = 'Odds'
            bet_history.append(
                f"👑type : {bet['type']}\n"
                f'🔴Color : {bet["color"]}\n'
                f'🔢Number : {num_type}\n'
                f'🤑Amount : {bet["amount"]}\n'
                f'📊Status : {bet["status"]}')
        elif bet['type'] == 'LIMBO':
            bet_history.append(
                f"👑type : {bet['type']}\n"
                f'⭐️target : {bet["target_multiplier"]}\n'
                f'🤑Amount : {bet["amount"]}\n'
                f'📊Status : {bet["status"]}')
        elif bet['type'] == 'BACCARAT':
            bet_history.append(
                f"👑type : {bet['type']}\n"
                f'🤑Amount : {bet["amount"]}\n'
                f'⭐️multiplier : {bet["multiplier"]}\n'
                f'📊Status : {bet["status"]}'
            )
    return "\n\n".join(bet_history)


def bets_options():
    """🎰 Betting options menu with interactive buttons."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🎯 Limbo', callback_data='limbo'), InlineKeyboardButton(
            text='🎡 Roulette', callback_data='roulette')],
        [InlineKeyboardButton(text='🎰 Baccarat', callback_data='baccarat')],
        [InlineKeyboardButton(text='🔙 Back to Main Menu',
                              callback_data='back_to_main_menu')]
    ])


def roulette_options():
    """Roulette bet target options with emojis"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🎲 Odds', callback_data='odds'), InlineKeyboardButton(
            text='🔢 Evens', callback_data='evens')],
        [InlineKeyboardButton(text='⚫ Black', callback_data='black'), InlineKeyboardButton(
            text='🔴 Red', callback_data='red')],
        [InlineKeyboardButton(text='🔙 Back to options',
                              callback_data='back_to_main_menu')]
    ])
