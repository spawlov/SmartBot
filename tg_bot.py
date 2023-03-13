import os

import telebot

from dotenv import load_dotenv, find_dotenv

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    tg_bot = telebot.TeleBot(os.getenv('TG_BOT_TOKEN'))


    @tg_bot.message_handler(commands=['start'])
    def reply_start(message: telebot.types.Message):
        tg_bot.send_message(message.chat.id, 'Здравствуйте')


    @tg_bot.message_handler(content_types=['text'])
    def echo(message: telebot.types.Message):
        tg_bot.send_message(message.chat.id, message.text)

    tg_bot.polling(none_stop=True)
