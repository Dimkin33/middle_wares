"""Entry point for running the tennis score application using Waitress WSGI server."""

# serve.py

import logging
import sys

from waitress import serve

from src.tennis_score.app import app

# Настройка корневого логгера
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)-8s %(name)-21s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Вывод в консоль
        logging.FileHandler('tennis_app.log')  # Дополнительно запись в файл
    ]
)

# Настройка логгеров для различных модулей
for logger_name in ['controller', 'router', 'app']:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

# Отключим логи от wsgi и настроим уровень для waitress
logging.getLogger('wsgi').setLevel(logging.WARNING)  # Только предупреждения и ошибки
logging.getLogger('waitress').setLevel(logging.INFO)

# Настроим также логи для сервисных слоев и репозиториев
logging.getLogger('service').setLevel(logging.DEBUG)
logging.getLogger('repository').setLevel(logging.DEBUG)

serve(app, host='127.0.0.1', port=8080)

