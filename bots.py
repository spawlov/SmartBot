import os
from threading import Thread

from dotenv import load_dotenv, find_dotenv
from loguru import logger
from notifiers.logging import NotificationHandler

from modules.dialog_flow import intents_update
from modules.tg_bot import _tg_bot
from modules.vk_bot import _vk_bot

logger.remove()


def main():
    load_dotenv(find_dotenv())
    tg_handler_params = {
        'token': os.getenv('LOGGER_BOT_TOKEN'),
        'chat_id': int(os.getenv('ALLOWED_CHAT_ID'))
    }
    tg_handler = NotificationHandler('telegram', defaults=tg_handler_params)
    logger.add(
        'debug.log',
        format='{level}::{time}::{message}',
        level='DEBUG',
        rotation='0:00',
        compression='zip',
    )
    logger.add(
        'info.log',
        format='{level}::{time}::{message}',
        level='INFO',
        rotation='0:00',
        compression='zip',
    )
    logger.add(
        'error.log',
        format='{level}::{time}::{message}',
        level='ERROR',
        rotation='0:00',
        compression='zip',
    )
    logger.add(tg_handler, level='WARNING')
    intents_update()
    Thread(target=_vk_bot).start()
    Thread(target=_tg_bot).start()


if __name__ == '__main__':
    main()
