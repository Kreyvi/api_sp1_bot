import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, можно приступать к следующему ' 
                   'уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {
        'Authorization': 'OAuth AgAAAAACsVOaAAYckYamRqsCLU5hjtNbE_aRGfI'
    }
    params = {'from_date': current_timestamp}
    homework_statuses = requests.get(API_URL, params=params, headers=headers)
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.info('Работа началась')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]), bot
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)  # опрашивать раз в пять минут
        except Exception as error:
            logging.error(error, exc_info=True)
            print(f'Бот столкнулся с ошибкой: {error}')
            time.sleep(5)


if __name__ == '__main__':
    main()
