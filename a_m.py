#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from functools import partial
import random
import logging
import os
import kai
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, chat, replymarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.error import TelegramError, BadRequest, Unauthorized


GROUP_TO_ECHO_TO_FILENAME = "echo_to_group_ids.csv"
GROUP_TO_ECHO_DICT = {}
UPDATE_HISTORY_FILENAME = "update_history.txt"


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def init_group_to_echo(filename, bot):
    try:
        with open(filename) as file:
            for line in file:
                values = line.split(",")
                group_id = int(values[0])
                group_name = values[1]
                add_group_to_echo_dict(group_id, bot)
    except:
        print("Something went wrong when reading group_to_echo")


def is_chat_id_in_group(chat_id):
    return chat_id in GROUP_TO_ECHO_DICT


def is_user_in_group(bot, group_id, chat_id):
    try:
        member_status = bot.get_chat_member(group_id, chat_id).status.lower()
        return member_status in ["administrator", "creator", "member"]
    except (BadRequest, Unauthorized):
        remove_group_from_echo_dict(group_id)
        print(f"Removed group from list")
        return False


def get_group_echo_dict():
    return GROUP_TO_ECHO_DICT


def add_group_to_echo_dict(group_id, bot):
    GROUP_TO_ECHO_DICT[group_id] = bot.get_chat(group_id).title[:45]


def remove_group_from_echo_dict(group_id):
    success = GROUP_TO_ECHO_DICT.pop(group_id)
    return bool(success)


def update_group_echo_file():
    with open(GROUP_TO_ECHO_TO_FILENAME, "w", encoding="utf-8") as file:
        stringify_dict = [f"{group_id},{group_name}\n" for group_id, group_name in GROUP_TO_ECHO_DICT.items()]
        file.writelines(stringify_dict)


def refresh_group_name(bot):
    for group_id in GROUP_TO_ECHO_DICT:
        add_group_to_echo_dict(group_id, bot)


def get_keyboard_format(chat_id, m_type, bot):
    group_echo_dict = get_group_echo_dict()
    user_in_list = {group_id:group_name for group_id, group_name in group_echo_dict.items() if is_user_in_group(bot, group_id, chat_id)}

    keyboard = []
    for group_id, group_name in user_in_list.items():
        output =f"{group_id},{group_name},{m_type}"
        keyboard.append([InlineKeyboardButton(group_name, callback_data=output)])

    return keyboard


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!'
    )


def group_start(update: Update, context: CallbackContext) -> None:
    """Add group_id to reading file"""
    group_id = update.message.chat_id

    if group_id > 0:
        text = "Doesn't look like you are in a group 🤔"
    elif is_chat_id_in_group(group_id):
        text = "Your group is already in the list"
    else:
        add_group_to_echo_dict(group_id, context.bot)
        text = "I have added your group into my list"
        update_group_echo_file()

    context.bot.send_message(chat_id=group_id, text=text)


def group_remove(update: Update, context: CallbackContext) -> None:
    """Remove group_id from file"""
    group_id = update.message.chat_id
    text = ""
    if group_id < 0:
        if not is_chat_id_in_group(group_id):
            text = "Your group isn't in my list"
        elif group_id < 0:
            remove_group_from_echo_dict(group_id)
            update_group_echo_file()
            text = "Removed your group from my list"
    else:
        text = "This place isn't a group"
    context.bot.send_message(chat_id=group_id, text=text)


def group_status(update: Update, context: CallbackContext) -> None:
    """Check if the current group in the list"""
    group_id = update.message.chat_id

    if group_id < 0:
        if is_chat_id_in_group(group_id):
            text = "Your group is in my list!"
        else:
            text = "Your group is NOT in my list!!"
    else:
        text = "This isn't a group!!"

    context.bot.send_message(chat_id=group_id, text=text)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Send me your message directly!')


def add_group_id_if_not_in_echo_list(update: Update, context: CallbackContext) -> None:
    try:
        chat_id = update.message.chat_id
    except AttributeError:
        chat_id = update.edited_message.chat_id

    if chat_id < 0:
        add_group_to_echo_dict(chat_id, context.bot)
        update_group_echo_file()


def echo(update: Update, context: CallbackContext, m_type) -> None:
    """Echo the user message/photo/video"""
    try:
        chat_id = update.message.chat_id
    except AttributeError:
        chat_id = update.edited_message.chat_id
        m_type = "edited_message"
    add_group_id_if_not_in_echo_list(update, context)

    if m_type == "message":
        context.user_data["message"] = update.message.text
    elif m_type == "edited_message":
        pass
    else:
        attribute_value = getattr(update.message, m_type)
        if isinstance(attribute_value, list):
            attribute_value = attribute_value[-1]
        context.user_data["message"] = attribute_value.file_id

    if update.message.chat.type.lower() == "private":
        keyboard = get_keyboard_format(chat_id, m_type, context.bot)
        if len(keyboard) > 0:
            reply_markup=InlineKeyboardMarkup(keyboard)
            text=f"Which group would you like to send your {m_type} to?"
            context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
            refresh_group_name(context.bot)
        else:
            text=f"I can't find any group that we are in together!"
            context.bot.send_message(chat_id=chat_id, text=text)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    group_id, group_name, m_type = query.data.split(",")
    if m_type == "kai":
        kai.button_callback_query()
    else:
        output = context.user_data["message"]
        method = f"send_{m_type}"
        getattr(context.bot, method)(group_id, output)

        query.edit_message_text(text=f"You sent your {m_type.replace('_',' ')} to {group_name}")
