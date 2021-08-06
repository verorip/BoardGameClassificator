import logging
import os
import io
import pickle
from Game import *
from emoji import emojize
from name_comparator import *
from Error_Handler import *

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

is_busy = False


class Custom_Handler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self, level=logging.INFO)
        self.chat_id = '128856686'

    def emit(self, log_record: logging.LogRecord):
        global is_busy
        log_message = self.format(log_record)
        # print(log_message)
        # Do stuff here...
        if bot_updater is not None and log_record.levelname != 'INFO':
            #print('\n\n\n\n\n\n\n\n\n\n\n\n', log_message)
            if len(log_message) >= 4096:
                idx = 0
                while idx < len(log_message):
                    bot_updater.bot.sendMessage(chat_id=self.chat_id, text=log_message[idx:(
                        idx + 4096 if idx + 4096 <= len(log_message) else len(log_message))])
                    idx += 4096
            else:
                bot_updater.bot.sendMessage(chat_id=self.chat_id, text=log_message)
        elif log_record.levelname == 'INFO' and 'Removed job ' in log_message:
            is_busy=False

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO, handlers=[
        logging.StreamHandler(),
        Custom_Handler()
    ]
)
emoji_medals = [emojize(":1st_place_medal:", use_aliases=True), emojize(":2nd_place_medal:", use_aliases=True),
                emojize(":3rd_place_medal:", use_aliases=True)]

logger = logging.getLogger(__name__)
# logger.addHandler(Custom_Handler())
# logger.propagate = False
games_list = list()

FIRST, SECOND, THIRD, FOURTH, FIFTH, SIXTH = range(6)
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN = range(7)

# orrendo, da cambiare
tmp_game = [' ', ' ']


def dyn_string(index, val, max):
    if index > max: return ''
    return '{} volte {}, '.format(val[index - 1],
                                  emoji_medals[index - 1] if index <= 3 else (str(index) + '°')) + dyn_string(index + 1,
                                                                                                              val, max)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_photo(open('logo/logo.jpg', 'rb'), caption='Board Game Geek Bot è in funzione! #BossCulo')


def save():
    pickle.dump(games_list, open('data.pickle', 'wb'))


def check_game(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text('Inserire Nome Del Gioco')
    return ONE


def check_size(update: Update, context: CallbackContext):
    tmp_game[0] = update.message.text
    update.message.reply_text('Inserire giocatori massimi')
    return TWO


def insert_game(update: Update, context: CallbackContext):
    global tmp_game, is_busy
    tmp_game[1] = update.message.text
    if tmp_game[0] not in [i.get_Name() for i in games_list]:
        x = Game(tmp_game[0], tmp_game[1])
        games_list.append(Game(tmp_game[0], tmp_game[1]))
        update.message.reply_text('Gioco Aggiunto!')
        save()
    else:
        update.message.reply_text('Gioco Già presente!')

    tmp_game = [' ', ' ']
    is_busy=False
    return ConversationHandler.END


def commands(update: Update, context: CallbackContext):
    global is_busy
    if is_busy:
        update.message.reply_text('\n Bot impegnato con un altro comando')
        update.message.delete()
        return
    keyboard = [
        [InlineKeyboardButton("Add Game", callback_data=str(FIRST))],
        [InlineKeyboardButton("Get Stats", callback_data=str(SECOND))],
        [InlineKeyboardButton("Update Game", callback_data=str(FIFTH))],
        [InlineKeyboardButton("Show Stored Games", callback_data=str(SIXTH))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_photo(open('logo/logo.jpg', 'rb'), caption='Commands:',
                               reply_markup=reply_markup)
    is_busy = True


def check_stats(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("By Game", callback_data=str(THIRD))],
        [InlineKeyboardButton("By Player", callback_data=str(FOURTH))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    query.edit_message_reply_markup(reply_markup)
    return THREE


def get_game_stats(update: Update, context: CallbackContext):
    global is_busy
    msg = ''
    # if update.message.text.lower() in [i.get_Name().lower() for i in games_list]:
    for i in games_list:
        if i.check_name(update.message.text.lower()):
            for key, val in i.get_users_stats().items():
                msg += '{} è arrivato '.format(key) + dyn_string(1, val, i.get_max_players())[:-2] + '\n\n'
            if len(msg) >= 1:
                update.message.reply_text(msg)
            else:
                update.message.reply_text('Non ci sono dati per ora')
            is_busy = False
            return ConversationHandler.END
    update.message.reply_text('Non ci sono giochi in lista chiamati {}'.format(update.message.text))
    # update.message.delete()
    is_busy = False
    return ConversationHandler.END


def get_player_stats(update: Update, context: CallbackContext):
    global is_busy
    msg = 'le statistiche di ' + update.message.text + ' sono:\n\n'
    stats = ''
    for x in games_list:
        r = x.get_user_stats(update.message.text)
        if r is not None:
            stats += 'In _' + x.get_Name() + '_:  ' + dyn_string(1, r, x.get_max_players()) + '\n\n'
    if len(stats) < 1:
        update.message.reply_text('Il giocatore {} non ha ancora giocato'.format(update.message.text))
    else:
        update.message.reply_text(msg + stats, parse_mode=ParseMode.MARKDOWN)
    update.message.delete()
    is_busy = False
    return ConversationHandler.END


def select_game(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text('Inserire Nome Del Gioco')
    query.message.delete()
    return FOUR


def select_player(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text('Inserire Nome Del Giocatore')
    query.message.delete()
    return FIVE


def select_update_game(update: Update, context: CallbackContext):
    global tmp_game, is_busy
    if update.message.text.lower() in [i.get_Name().lower() for i in games_list]:
        for j in games_list:
            if j.get_Name().lower() == update.message.text.lower():
                tmp_game[0] = j
        update.message.reply_text('inserire nome giocatore e posizione separati da spazio (e.g. Mario 1)')
        update.message.delete()
        return SEVEN
    else:
        update.message.reply_text('nessun gioco trovato col nome {}'.format(update.message.text))
        update.message.delete()
        is_busy = False
        return ConversationHandler.END


def upd_name(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text('Inserire Nome Del Gioco', timeout=20000)
    query.message.delete()
    return SIX


def quit_conversation(update: Update, context: CallbackContext):
    global is_busy
    is_busy = False
    return ConversationHandler.END


def update_game(update: Update, context: CallbackContext):
    global tmp_game, is_busy
    msg = update.message.text.split()
    if len(msg) < 2 or not any(char.isdigit() for char in msg):
        tmp_game = [' ', ' ']
        is_busy = False
        return ConversationHandler.END
    else:
        tmp_game[0].update_user(msg[0], int(msg[1]))
        update.message.reply_text('inserire il successivo nome giocatore e posizione separati da spazio (e.g. Mario 1)')
        # update.message.delete(timeout=2000)
        save()
        return SEVEN


def show_games(update: Update, context: CallbackContext):
    msg = ''
    query = update.callback_query
    query.answer()
    for i in games_list:
        msg += i.get_Name() + '\n'
    query.message.reply_text(msg)
    query.message.delete()


def main() -> None:
    global bot_updater
    try:
        bot_updater = Updater(open('key.txt', 'r').readline(), use_context=True) if 'BoardGame_Key' not in os.environ \
            else Updater(os.environ.get('BoardGame_Key'), use_context=True)
    except Exception as e:
        print(e)
        return
    dispatcher = bot_updater.dispatcher

    dispatcher.add_handler(CommandHandler(['command', 'commands'], commands))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(check_game, pattern='^' + str(FIRST) + '$'),
                      CallbackQueryHandler(check_stats, pattern='^' + str(SECOND) + '$'),
                      CallbackQueryHandler(upd_name, pattern='^' + str(FIFTH) + '$'),
                      CallbackQueryHandler(show_games, pattern='^' + str(SIXTH) + '$')],
        states={
            ONE: [MessageHandler(Filters.text, callback=check_size)],
            TWO: [MessageHandler(Filters.text, callback=insert_game)],
            THREE: [
                CallbackQueryHandler(select_game, pattern='^' + str(THIRD) + '$'),
                CallbackQueryHandler(select_player, pattern='^' + str(FOURTH) + '$'),
            ],
            FOUR: [MessageHandler(Filters.text, callback=get_game_stats)],
            FIVE: [MessageHandler(Filters.text, callback=get_player_stats)],
            SIX: [MessageHandler(Filters.text, callback=select_update_game)],
            SEVEN: [MessageHandler(Filters.text, callback=update_game)]

        },
        conversation_timeout=10,
        fallbacks=[CommandHandler('quit', quit_conversation)],
    ))
    global games_list
    try:
        if os.stat("data.pickle").st_size > 0:
            games_list = pickle.load(open('data.pickle', 'rb'))
            for i in games_list:
                print(i.get_Name(), type(i))
        else:
            # debug
            games_list.append(Game('test', 4))
            games_list[0].update_user('capuz', 1)
            games_list[0].update_user('rick', 2)
            games_list[0].update_user('boss', 3)
            games_list[0].update_user('capuz', 1)
            games_list[0].update_user('rick', 3)
            games_list[0].update_user('boss', 2)
            games_list[0].update_user('capuz', 1)
            games_list[0].update_user('rick', 2)
            games_list[0].update_user('boss', 3)
            games_list[0].update_user('capuz', 1)
            games_list[0].update_user('rick', 2)
            games_list[0].update_user('boss', 3)
            games_list.append(Game('the mind', 4))
            games_list.append(Game('surviving mars', 9))
    except Exception as e:
        print(e)
        return

    bot_updater.start_polling()
    # bot_updater.bot.sendMessage(chat_id='128856686', text='Hello there!')
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    bot_updater.idle()


if __name__ == "__main__":
    main()
