import random

import requests
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from loguru import logger

from chat_bots.dialog_flow import detect_intent_texts


def vk_send_message(event, vk_api, project_id) -> None:
    session = f'vk-{event.user_id}'
    answer = detect_intent_texts(project_id, event.text, session)
    if answer.intent.is_fallback:
        return
    vk_api.messages.send(
        user_id=event.user_id,
        message=answer.fulfillment_text,
        random_id=random.randint(1, 1000)
    )


def vk_bot(project_id: str, vk_token: str) -> None:
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.warning('VK bot is running!')
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                vk_send_message(event, vk_api, project_id)
    except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
    ) as e:
        logger.error(e)
        logger.error('VK bot is down!')
