from functools import partial
import random
import logging
import os
import kai
import a_m
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, chat, replymarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from telegram.error import TelegramError, BadRequest


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    load_dotenv()
    updater = Updater(os.getenv("TOKEN"))
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    kai.init_kai_quotes()
    a_m.init_group_to_echo(a_m.GROUP_TO_ECHO_TO_FILENAME, updater.bot)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", a_m.start))
    dispatcher.add_handler(CommandHandler("gstart", a_m.group_start))
    # dispatcher.add_handler(CommandHandler("gremove", a_m.group_remove))
    dispatcher.add_handler(CommandHandler("gstatus", a_m.group_status))
    dispatcher.add_handler(CommandHandler("kai", kai.get_random_kai_quote))
    dispatcher.add_handler(CommandHandler("addkai", kai.add_kai_quote))
    dispatcher.add_handler(CommandHandler("delkai", kai.delete_kai_quote))
    # dispatcher.add_handler(CommandHandler("editkai", kai.edit_kai_quotes))
    dispatcher.add_handler(CommandHandler("help", a_m.help_command))

    # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.all, add_group_id_if_not_in_echo_list))
    dispatcher.add_handler(MessageHandler(Filters.update.message & ~Filters.command, partial(a_m.echo, m_type="message")))
    dispatcher.add_handler(MessageHandler(Filters.photo, partial(a_m.echo, m_type="photo")))
    dispatcher.add_handler(MessageHandler(Filters.video, partial(a_m.echo, m_type="video")))
    dispatcher.add_handler(MessageHandler(Filters.sticker, partial(a_m.echo, m_type="sticker")))
    dispatcher.add_handler(MessageHandler(Filters.voice, partial(a_m.echo, m_type="voice")))
    dispatcher.add_handler(MessageHandler(Filters.video_note, partial(a_m.echo, m_type="video_note")))
    dispatcher.add_handler(MessageHandler(Filters.animation, partial(a_m.echo, m_type="animation")))
    dispatcher.add_handler(MessageHandler(Filters.audio, partial(a_m.echo, m_type="audio")))
    dispatcher.add_handler(CallbackQueryHandler(a_m.button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
