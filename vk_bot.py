import os
import random
from time import sleep

import requests
from loguru import logger
from requests import Response
import vk_api as vk

from dialog_flow import detect_intent_texts


def vk_echo(peer_id: int, message: str) -> None:
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()
    answer = detect_intent_texts(os.getenv('PROJECT_ID'), message, bot='vk')
    if len(answer) > 0:
        vk_api.messages.send(
            peer_id=peer_id,
            message=answer,
            random_id=random.randint(1, 1000)
        )


def get_vk_session() -> [Response, None]:
    url = f'https://api.vk.com/method/messages.getLongPollServer'
    params = {
        'access_token': os.getenv('VK_TOKEN'),
        'v': '5.131',
    }
    try:
        response = requests.get(url=url, params=params)
        response.raise_for_status()
    except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
    ) as e:
        logger.error(e)
    else:
        if 'error' not in response.text:
            return response
        error = response.json()
        logger.error(error['error']['error_msg'])
        return


def vk_failed_handler(response: Response, params: dict) -> [dict, None]:
    failed = response.json()
    logger.info(failed)
    vk_session = get_vk_session()
    if not vk_session:
        logger.error('VK session failed!')
        return
    if failed['failed'] == 1:
        session = vk_session.json()
        params.update(ts=session['response']['ts'])
        logger.info('TS has been updated...')
        return params
    elif failed['failed'] == 2:
        session = vk_session.json()
        params.update(key=session['response']['key'])
        logger.info('KEY has been updated...')
        return params
    elif failed['failed'] == 3:
        session = vk_session.json()
        params.update(
            ts=session['response']['ts'],
            key=session['response']['key']
        )
        logger.info('TS and KEY has been updated...')
        return params
    elif failed['failed'] == 4:
        logger.error('Not valid version! VK bot is down!')
        return
    else:
        logger.info('Unknown error...')
        return params


def _vk_bot() -> None:
    vk_session = get_vk_session().json()
    if not vk_session:
        logger.error('VK session failed!')
        return
    server = vk_session['response']['server']
    url = f'https://{server}'
    params = {
        'act': 'a_check',
        'key': vk_session['response']['key'],
        'ts': vk_session['response']['ts'],
        'wait': 25,
        'version': 3,
    }
    logger.info('VK bot is running!')
    attempt_connect = 0
    while True:
        try:
            attempt_connect += 1
            response = requests.get(url=url, params=params)
            response.raise_for_status()
        except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
        ) as e:
            logger.error(e)
            logger.error(f'Pause: {60 * attempt_connect} sec.')
            sleep(60 * attempt_connect)
        else:
            if 'failed' in response.text:
                params = vk_failed_handler(response, params)
                if not params:
                    logger.error('VK bot is down!')
                    return
                continue
            attempt_connect = 0
            vk_answer = response.json()
            params.update(ts=vk_answer['ts'])
            if not len(vk_answer['updates']):
                continue
            list_index = 0 if len(vk_answer['updates']) == 1 else 1
            if vk_answer['updates'][list_index][0] == 4:
                vk_echo(
                    vk_answer['updates'][list_index][3],
                    vk_answer['updates'][list_index][5]
                )
