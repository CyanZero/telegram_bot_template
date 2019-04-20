# This is simple and easy telegram bots written in python3
# It comes with common functions and useful conversation mode:
# - command
# - coverstaion
# - button options
# - inline button options

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, Filters, RegexHandler
from telegram import ParseMode, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from enum import Enum, auto
from decimal import Decimal
import logging
import traceback
import subprocess
import requests
import json
import re
import os
import time

TEL_BOT_TOKEN = ""

# For the state machine of creating events, because conversation handlers are state machines
LANG = range(100, 200)
PYTHON, GO = range(300, 302)
options = ["PYTHON", "GO"]
url = 'https://github.com/CyanZero/telegram_bot_template'

help_text = 'Welcomes to telegram chat bot. \n' \
            'Supported Commands:\n\n' \
            '/help - How can I help?\n' \
            '\t/hello - Hello telegram! \n' \
            '\t/status - InlineButtonMode \n' \
            '\t/start - Start a conversation \n'


# ------ Common functions that can be moved to other util files
# Enum for keyboard buttons
class KeyboardEnum(Enum):
    BOT = auto()
    YES = auto()
    NO = auto()
    CANCEL = auto()

    def clean(self):
        return self.name.replace("_", " ")


def help(bot, update):
    """ Prints help text """

    logging.debug("Help")

    chat_id = update.message.chat.id
    # To heck user status
    # chat_str = str(chat_id)
    # if (not db.get(chat_str + '_quiet') or db.get(chat_str + '_adm') ==
    #         update.message.from_user.id):
    bot.sendMessage(chat_id=chat_id, text=help_text)


def conversation_cancel(bot, update, user_data):  # {
    logging.debug("canceled")
    bot.sendMessage(chat_id=update.message.chat.id, text="Invalid input or user canceled, type /help or other command to continue..")
    return ConversationHandler.END
# }


def checkTypePrivate(update):  # {
    return update.message.chat.type == 'private'
# }


def compose_response_button():  # {
    keyboard = []
    keyboard.append([KeyboardButton(KeyboardEnum.YES.clean()), KeyboardButton(KeyboardEnum.CANCEL.clean())])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

# }


def log_error(bot, update, error):  # {
    print("Error caught...")
    logging.error('Update "%s" caused error "%s"' % (update, error))
# }

# ------ Common functions ends


def status(bot, update):  # {
    logging.debug("status")
    chat_id = update.message.chat_id

    keyboard = []

    keyboard.append([InlineKeyboardButton(KeyboardEnum.BOT.clean(), callback_data=KeyboardEnum.BOT.clean())])
    reply_markup = InlineKeyboardMarkup(keyboard)

    keyboard.append([InlineKeyboardButton(KeyboardEnum.CANCEL.clean(), callback_data=KeyboardEnum.CANCEL.clean())])

    bot.sendMessage(chat_id=chat_id, text='Choose an option:', reply_markup=reply_markup)

    return
# }


def check_bot_status(bot, update):  # {
    callbackquery = update.callback_query

    bot.editMessageText(text="Checking status: %s" % callbackquery,
                        chat_id=callbackquery.message.chat_id,
                        message_id=callbackquery.message.message_id)

    msg = "I'm doing well, how about you?"
    time.sleep(5)

    bot.editMessageText(text=msg,
                        chat_id=callbackquery.message.chat_id,
                        message_id=callbackquery.message.message_id)
# }


def inline_button_callback(bot, update):  # {
    callbackquery = update.callback_query
    querydata = callbackquery.data

    if KeyboardEnum.CANCEL.clean() == querydata:
        bot.editMessageText(text="Canceled",
                            chat_id=callbackquery.message.chat_id,
                            message_id=callbackquery.message.message_id)

        return

    logging.info("Received callback: " + querydata)

    if KeyboardEnum.BOT.clean() == querydata:
        check_bot_status(bot, update)

    return
# }


def start(bot, update, user_data):  # {
    logging.debug("Start a conversation..")
    if not checkTypePrivate(update):
        update.message.reply_text("Please send this bot a private message.")
        return ConversationHandler.END

    reply_text = "Good, let's talk about:\n"

    i = 1
    keyboard = []
    inline_button = []
    for token in options:  # {
        reply_text += "\t%s.\t%s\n" % (str(i), token)

        inline_button.append(str(i))
        i += 1
    # }

    cancel_btn = [KeyboardButton(KeyboardEnum.CANCEL.clean())]
    keyboard.append(inline_button)
    keyboard.append(cancel_btn)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text(reply_text, reply_markup=reply_markup)

    return LANG
# }


def hello(bot, update):  # {
    chat_id = update.message.chat_id

    bot.sendMessage(chat_id=chat_id, text='Hello telegram! This is a simple comamnd')

    return
# }


def lang(bot, update, user_data):  # {
    logging.debug(user_data)
    logging.debug(update.message.text)

    selected_index = update.message.text

    choosen_lang = ""
    if int(selected_index) <= len(options):
        choosen_lang = options[int(selected_index) - 1]
    else:
        return conversation_cancel(bot, update, user_data)

    reply_text = ""
    if choosen_lang == "PYTHON":
        reply_text = "Good choice! I'm created using %s, which is easy and elegant, to find out more, please visit: %s" % (choosen_lang, url)
    elif choosen_lang == "GO":
        reply_text = "GOLANG is great! You should try out it now!"

    update.message.reply_text(reply_text)
    return ConversationHandler.END
# }


def main():  # {
    updater = Updater(TEL_BOT_TOKEN)
    dp = updater.dispatcher
    # log all errors
    dp.add_error_handler(log_error)

    dp.add_handler(CommandHandler('help', help))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],
        states={
            LANG: [RegexHandler('^(\d)$',
                                lang,
                                pass_user_data=True)]
        },
        fallbacks=[MessageHandler(Filters.text, conversation_cancel, pass_user_data=True)]
    ))

    dp.add_handler(CommandHandler('hello', hello))
    dp.add_handler(CommandHandler('status', status))
    dp.add_handler(CallbackQueryHandler(inline_button_callback))

    updater.start_polling()
    logging.info("Chat bot start listening...")
    updater.idle()
# }


if __name__ == '__main__':

    token = os.environ['TEL_BOT_TOKEN']

    if token == "":
        logging.error("Panic! Not found valid tel bot token")
        exit()
    # Read the config from local env
    TEL_BOT_TOKEN = token

    main()
