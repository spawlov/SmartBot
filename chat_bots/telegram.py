from loguru import logger
from telegram import Update
from telegram.ext import (
    CallbackContext,
    Updater,
    CommandHandler,
    MessageHandler,
    Filters
)

from chat_bots.dialog_flow import detect_intent_texts


def tg_start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    firstname = user.first_name if user.first_name else ''
    lastname = user.last_name if user.last_name else ''
    update.message.reply_text(
        f'Здравствуйте, {firstname} {lastname}!'
    )


def tg_send_message(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        detect_intent_texts(
            context.bot_data['project_id'],
            update.message.text,
            f'tg-{update.effective_user.id}'
        ).fulfillment_text
    )


def tg_bot(project_id, tg_token) -> None:
    bot = Updater(tg_token)
    dispatcher = bot.dispatcher
    dispatcher.bot_data['project_id'] = project_id
    dispatcher.add_handler(CommandHandler("start", tg_start))
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            tg_send_message
        )
    )
    bot.start_polling()
    logger.warning('Telegram bot is running!')
