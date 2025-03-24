from telegram.ext import (
    ApplicationBuilder,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from telegrambot.handlers.deposit_withdraw_handler import (
    deposit_start,
    deposit_amount_handler,
    withdraw_start,
    withdraw_amount_handler
)
from telegrambot.utils import (
    DEPOSIT_AMOUNT,
    WITHDRAW_AMOUNT,
    NUMBER_COLOR_SELECTION,
    AMOUNT,
    CONFIRM,
    BET_TYPE
)
from telegrambot.handlers.start_handler import (
    start,
    main_menu_callback
)
from telegrambot.handlers.bet_handler import (
    bet_menu_callback_handler
)

from telegrambot.handlers.limbo_bet_handler import (
    limbo_bet_start,
    limbo_bet_handler,
    bet_amount_handler,
    confirm_limbo_bet
)
from telegrambot.handlers.roulette_bet_handler import (
    roulette_bet_start,
    roulette_bet_selection_handler,
    get_roulette_amount,
    roulette_bet_confirm
)
from telegrambot.handlers.baccarat_bet_handler import (
    baccarat_bet_start,
    amount_handler_baccarat,
    baccarat_game
)
import logging


def main(bot_token):
    app = ApplicationBuilder().token(bot_token).build()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    deposit_withdraw_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(deposit_start, pattern='^deposit$'),
            CallbackQueryHandler(withdraw_start, pattern='^withdraw$')
        ],
        states={
            DEPOSIT_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               deposit_amount_handler)
            ],
            WITHDRAW_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               withdraw_amount_handler)
            ]
        },
        fallbacks=[],
    )

    limbo_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(limbo_bet_start, pattern="^limbo$")
        ],
        states={
            NUMBER_COLOR_SELECTION: [CallbackQueryHandler(limbo_bet_handler)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bet_amount_handler)],
            CONFIRM: [CallbackQueryHandler(
                confirm_limbo_bet, pattern="^(confirm_limbo|cancel)$")]
        },
        fallbacks=[]
    )

    roulette_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(roulette_bet_start, pattern='^roulette$')
        ],
        states={
            NUMBER_COLOR_SELECTION: [
                CallbackQueryHandler(
                    roulette_bet_selection_handler, pattern="^(odds|evens|black|red)$")
            ],
            AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               get_roulette_amount)
            ],
            CONFIRM: [
                CallbackQueryHandler(roulette_bet_confirm,
                                     pattern="^(cancel|confirm)$")
            ]
        },
        fallbacks=[]
    )
    baccarat_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(baccarat_bet_start, pattern='^baccarat$')
        ],
        states={
            BET_TYPE:[
                CallbackQueryHandler(amount_handler_baccarat, pattern='^(player|banker|tie|cancel)$')
            ],
            AMOUNT:[
                MessageHandler(filters.TEXT & ~filters.COMMAND, baccarat_game)
            ]
        },
        fallbacks=[]
    )

    app.add_handler(deposit_withdraw_conv)
    app.add_handler(roulette_conv)
    app.add_handler(limbo_conv)
    app.add_handler(baccarat_conv)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(main_menu_callback,
                                         pattern='^bet|account_status|back_to_main_menu$'))
    app.add_handler(CallbackQueryHandler(bet_menu_callback_handler,
                                         pattern="^football|limbo|roulette|back_to_bet_menu$"))

    app.run_polling()
