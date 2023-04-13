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

from dialog_flow import detect_intent_texts


def tg_start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f'Здравствуйте, {user.first_name} {user.last_name}!'
    )


def tg_echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        detect_intent_texts(os.getenv('PROJECT_ID'), update.message.text)
    )


def _tg_bot() -> None:
    tg_bot = Updater(os.getenv('TG_BOT_TOKEN'))
    dispatcher = tg_bot.dispatcher
    dispatcher.add_handler(CommandHandler("start", tg_start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, tg_echo)
    )
    tg_bot.start_polling()
    logger.info('Telegram bot is running!')
