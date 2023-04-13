import os
import uuid

import requests
from google.cloud import dialogflow
from google.cloud.dialogflow_v2 import Intent
from loguru import logger


def detect_intent_texts(project_id: str, text: str, bot: str = 'tg') -> str:
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, str(uuid.uuid4()))
    text_input = dialogflow.TextInput(
        {
            'text': text,
            'language_code': 'ru-RU',
        }
    )
    query_input = dialogflow.QueryInput(
        {
            'text': text_input,
        }
    )
    response = session_client.detect_intent(
        request={
            'session': session,
            'query_input': query_input,
        }
    )
    if bot == 'vk' and response.query_result.intent.is_fallback:
        return ''
    return response.query_result.fulfillment_text


def get_intents_list(project_id: str) -> list:
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(
        request={
            'parent': parent,
        }
    )
    return [intent.display_name for intent in intents]


def create_intent(
        project_id: str,
        display_name: str,
        training_phrases_parts: list,
        message_texts: str
) -> Intent:
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(
            {
                'parts': [part],
            }
        )
        training_phrases.append(training_phrase)
    text = dialogflow.Intent.Message.Text(
        {
            'text': [message_texts],
        }
    )
    message = dialogflow.Intent.Message(
        {
            'text': text
        }
    )

    intent = dialogflow.Intent(
        {
            'display_name': display_name,
            'training_phrases': training_phrases,
            'messages': [message],
        }
    )
    return intents_client.create_intent(
        request={
            'parent': parent,
            'intent': intent,
        }
    )


def intents_update() -> None:
    project_id = os.getenv('PROJECT_ID')
    intents_list = get_intents_list(project_id)
    try:
        response = requests.get(os.getenv('QUESTIONS_URL'))
        response.raise_for_status()
    except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
    ) as e:
        logger.error(e)
    else:
        questions = response.json()
        for display_name, items in questions.items():
            if display_name not in intents_list:
                result = create_intent(
                    project_id,
                    display_name,
                    items['questions'],
                    items['answer']
                )
                logger.info(f'Intent created: {result}')
