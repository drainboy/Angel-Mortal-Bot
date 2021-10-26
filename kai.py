import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, chat, replymarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.error import TelegramError, BadRequest

KAI_QUOTES_LIST = []
KAI_QUOTES_FILENAME = "kai_quotes.txt"
KAI_DELETED_QUOTES_FILENAME = "kai_deleted_quotes.txt"

def button_callback_query():
    kai_quotes = get_kai_quotes()
    kai_quote_to_delete = kai_quotes[int(group_id)].strip()

    with open(KAI_QUOTES_FILENAME) as file:
            with open("tempfile","w") as output:
                for line in file:
                    if line != kai_quote_to_delete:
                        output.write(line)

    with open(KAI_DELETED_QUOTES_FILENAME, "w") as file:
        file.write(kai_quote_to_delete+"\n")

    os.replace("tempfile", KAI_QUOTES_FILENAME)
    text=f"\"{kai_quote_to_delete}\" is forever gone!!!"
    context.bot.send_message(chat_id=group_name, text=text)


def init_kai_quotes():
    with open(KAI_QUOTES_FILENAME) as file:
        for line in file:
            KAI_QUOTES_LIST.append(line.strip())


def get_kai_quotes():
    return KAI_QUOTES_LIST


def add_kai_quote(update: Update, context: CallbackContext) -> None:
    quote = " ".join(context.args)
    if quote:
        kai_quotes_lower_list = [quote.lower() for quote in get_kai_quotes()]
        if quote.lower() not in kai_quotes_lower_list:
            with open(KAI_QUOTES_FILENAME, "a") as file:
                file.write(quote+"\n")

        update.message.reply_text(f"\"{quote}\" added!!")
    else:
        update.message.reply_text(f"Invalid kai quote ;(")


def delete_kai_quote(update: Update, context: CallbackContext) -> None:
    kai_quotes_list = get_kai_quotes()
    chat_id = update.message.chat_id

    if chat_id in [51128963]:
        keyboard = []

        for index in range(len(kai_quotes_list)):
            quote = kai_quotes_list[index]
            data = f"{index},{chat_id},kai"
            keyboard.append([InlineKeyboardButton(quote,callback_data=data)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text=f"Which kai quote would you like to delete?", reply_markup=reply_markup)


def edit_kai_quotes(update: Update, context: CallbackContext) -> None:
    pass


def get_random_kai_quote(update: Update, context: CallbackContext) -> None:
    kai_quotes = get_kai_quotes()
    print(kai_quotes)
    random_kai_quote = random.choice(kai_quotes)
    print(random_kai_quote)
    update.message.reply_text(random_kai_quote)
