import os
from threading import Thread

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from notifiers.logging import NotificationHandler

from dialog_flow import intents_update
from tg_bot import _tg_bot
from vk_bot import _vk_bot


def main():
    load_dotenv(find_dotenv())
    tg_handler_params = {
        'token': os.getenv('LOGGER_BOT_TOKEN'),
        'chat_id': int(os.getenv('ALLOWED_CHAT_ID'))
    }
    tg_handler = NotificationHandler('telegram', defaults=tg_handler_params)
    logger.add(tg_handler, level='INFO')
    intents_update()
    Thread(target=_vk_bot).start()
    Thread(target=_tg_bot).start()


if __name__ == '__main__':
    main()
