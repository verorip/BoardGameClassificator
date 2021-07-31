import logging
import os
import io
import pickle
from Game import *

from telegram import Update, Chat, ChatMember, ParseMode, ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    ChatMemberHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler
)

bot_updater = None

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

games_list = list()

FIRST, SECOND = range(2)
ONE, TWO, THREE = range(3)

tmp_game = [' ', ' ']


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_photo(open('logo/logo.jpg', 'rb'), caption='Board Game Geek Bot è in funzione! #BossCulo')


def add_game(update: Update, context: CallbackContext) -> None:
    if len(update.message.text.split()) < 3:
        update.message.reply_text('You need to insert game name')
    games_list.append(Game(update.message.text.split()[1]))


def get_game_stats(update: Update, context: CallbackContext) -> None:
    pass


def commands(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Add Game", callback_data=str(FIRST))],
        [InlineKeyboardButton("Get Stats", callback_data=str(SECOND))]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_photo(open('logo/logo.jpg', 'rb'), caption='Commands (buttons not working for now):',
                               reply_markup=reply_markup)
    return ONE


def update_game(update: Update, context: CallbackContext) -> None:
    pass


def check_game(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text('Inserire Nome Del Gioco')
    return TWO
    #update.message.reply_text('Inserire Nome del gioco')


def check_size(update: Update, context: CallbackContext):
    tmp_game[0] = update.message.text
    update.message.reply_text('Inserire giocatori massimi')
    return THREE


def insert_game(update: Update, context: CallbackContext):
    tmp_game[1] = update.message.text
    if tmp_game[0] not in [i.get_Name() for i in games_list]:
        games_list.append(Game(tmp_game[0], tmp_game[1]))
        update.message.reply_text('Gioco Aggiunto!')
    else:
        update.message.reply_text('Gioco Già presente!')
    return ConversationHandler.END


def quit(update: Update, context: CallbackContext):
    return ConversationHandler.END


def main() -> None:
    global bot_updater
    try:
        bot_updater = Updater(open('key.txt', 'r').readline(), use_context=True) if 'BoardGame_Key' not in os.environ \
            else Updater(os.environ.get('BoardGame_Key'), use_context=True)
    except Exception as e:
        print(e)
        return
    dispatcher = bot_updater.dispatcher
    dispatcher.add_handler(CommandHandler("stats", get_game_stats))
    dispatcher.add_handler(CommandHandler("upd", update_game))

    #dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.text, commands)],
        states={
            ONE: [
                CallbackQueryHandler(check_game, pattern='^' + str(FIRST) + '$'),
                CallbackQueryHandler(get_game_stats, pattern='^' + str(SECOND) + '$'),
            ],
            TWO: [MessageHandler(Filters.text, callback=check_size)],
            THREE: [MessageHandler(Filters.text, callback=insert_game)]

        },
        fallbacks=[CommandHandler('quit', quit)]
    ))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, commands))
    global games_list
    try:
        if os.stat("data.pickle").st_size > 0:
            games_list = pickle.load(open('data.pickle', 'rb'))
    except Exception as e:
        print(e)
        return
    bot_updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    bot_updater.idle()


if __name__ == "__main__":
    main()
