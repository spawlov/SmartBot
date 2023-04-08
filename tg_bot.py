import os
import uuid

from dotenv import load_dotenv, find_dotenv
from google.cloud import dialogflow
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f'Здравствуйте, {user.first_name} {user.last_name}!'
    )


def echo(update: Update, context: CallbackContext) -> None:
    project_id = os.getenv('PROJECT_ID')
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, str(uuid.uuid4()))
    text_input = dialogflow.TextInput(
        text=update.message.text,
        language_code='ru-RU'
    )
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    answer = response.query_result.fulfillment_text
    update.message.reply_text(answer)


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
