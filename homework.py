import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

API_PARAMS = {
    'PRAKTIKUM_TOKEN': os.getenv('PRAKTIKUM_TOKEN'),
    'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN'),
    'CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
}
API_METHODS = {
    'homework': 'user_api/homework_statuses/'
}
API_URL = 'https://praktikum.yandex.ru/api/'
STATUSES = {
    'rejected': 'К сожалению в работе нашлись ошибки.',
    'approved': ('Ревьюеру всё понравилось, можно приступать к следующему'
                 ' уроку.'),
    'reviewing': 'Работа взята в ревью'
}
logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)


def parse_homework_status(homework):
    if 'homework_name' not in homework or 'status' not in homework:
        return 'Произошла ошибка'
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in STATUSES:
        return 'Что-то пошло не так, поэтому мы не знаем что с вашей работой'
    verdict = STATUSES[homework_status]
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp=None):
    if not isinstance(current_timestamp, (int, float)) or (
            current_timestamp is None):
        current_timestamp = time.time()
    headers = {
        'Authorization': 'OAuth ' + API_PARAMS['PRAKTIKUM_TOKEN']
    }
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            url=API_URL+API_METHODS['homework'],
            params=params,
            headers=headers
        )
    except (
            requests.HTTPError,
            requests.ConnectionError,
            requests.Timeout
    ) as error:
        logging.error(error, exc_info=True)
        raise
    except requests.RequestException as error:
        logging.error(error, exc_info=True)
        return {}
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(
        chat_id=API_PARAMS['CHAT_ID'],
        text=message
    )


def main():
    logging.info('Работа началась')
    bot = telegram.Bot(token=API_PARAMS['TELEGRAM_TOKEN'])
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks') is not None:
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)
        except Exception as error:
            logging.error(error, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
