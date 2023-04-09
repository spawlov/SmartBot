
import os

import requests
from dotenv import load_dotenv, find_dotenv
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from extensions import detect_intent_texts, get_intents_list, create_intent


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f'Здравствуйте, {user.first_name} {user.last_name}!'
    )


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        detect_intent_texts(os.getenv('PROJECT_ID'), update.message.text)
    )


def main() -> None:
    load_dotenv(find_dotenv())
    tg_bot = Updater(os.getenv('TG_BOT_TOKEN'))
    project_id = os.getenv('PROJECT_ID')

    intents_list = get_intents_list(project_id)
    questions = requests.get(os.getenv('QUESTIONS_URL')).json()
    for display_name, items in questions.items():
        if display_name not in intents_list:
            result = create_intent(
                project_id,
                display_name,
                items['questions'],
                items['answer']
            )
            # print(f'Intent created: {result}')

    dispatcher = tg_bot.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, echo)
    )

    tg_bot.start_polling()
    tg_bot.idle()


if __name__ == '__main__':
    main()
