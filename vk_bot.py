import os
import random

from dotenv import load_dotenv, find_dotenv
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from extensions import detect_intent_texts


def echo(event, vk_api):
    answer = detect_intent_texts(os.getenv('PROJECT_ID'), event.text, bot='vk')
    if len(answer) > 0:
        vk_api.messages.send(
            user_id=event.user_id,
            message=answer,
            random_id=random.randint(1, 1000)
        )


def main():
    load_dotenv(find_dotenv())
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)


if __name__ == '__main__':
    main()
