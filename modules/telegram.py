import os

from loguru import logger
from telegram import Update
from telegram.ext import (
    CallbackContext,
    Updater,
    CommandHandler,
    MessageHandler,
    Filters
)

from modules.dialog_flow import detect_intent_texts


def tg_start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    firstname = user.first_name if user.first_name else ''
    lastname = user.last_name if user.last_name else ''
    update.message.reply_text(
        f'Здравствуйте, {firstname} {lastname}!'
    )


def tg_send_message(update: Update, context: CallbackContext) -> None:
    """PROJECT_ID is taken from environment variables,
    since it is impossible to pass it as a positional argument """
    update.message.reply_text(
        detect_intent_texts(
            os.getenv('PROJECT_ID'),
            update.message.text,
            f'tg-{update.effective_user.id}'
        ).fulfillment_text
    )


def tg_bot(tg_token) -> None:
    bot = Updater(tg_token)
    dispatcher = bot.dispatcher
    dispatcher.add_handler(CommandHandler("start", tg_start))
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            tg_send_message
        )
    )
    bot.start_polling()
    logger.warning('Telegram bot is running!')
