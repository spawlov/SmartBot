import os

from dotenv import load_dotenv, find_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main() -> None:
    load_dotenv(find_dotenv())
    tg_bot = Updater(os.getenv('TG_BOT_TOKEN'))

    dispatcher = tg_bot.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, echo)
    )

    tg_bot.start_polling()
    tg_bot.idle()


if __name__ == '__main__':
    main()
