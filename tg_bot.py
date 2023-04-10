import os

import requests
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from notifiers.logging import NotificationHandler
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from extensions import detect_intent_texts, get_intents_list, create_intent

logger.remove()


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
    tg_handler_params = {
        'token': os.getenv('LOGGER_BOT_TOKEN'),
        'chat_id': int(os.getenv('ALLOWED_CHAT_ID'))
    }
    tg_handler = NotificationHandler('telegram', defaults=tg_handler_params)
    logger.add(tg_handler, level='INFO')

    project_id = os.getenv('PROJECT_ID')
    intents_list = get_intents_list(project_id)
    try:
        questions = requests.get(os.getenv('QUESTIONS_URL')).json()
    except requests.exceptions.ReadTimeout as e:
        logger.error(e)
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
    except requests.exceptions.HTTPError as e:
        logger.error(e)
    else:
        for display_name, items in questions.items():
            if display_name not in intents_list:
                result = create_intent(
                    project_id,
                    display_name,
                    items['questions'],
                    items['answer']
                )
                logger.info(f'Intent created: {result}')
    finally:
        dispatcher = tg_bot.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, echo)
        )
        tg_bot.start_polling()
        tg_bot.idle()


if __name__ == '__main__':
    main()
