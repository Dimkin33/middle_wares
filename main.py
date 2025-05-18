"""Entry point for running the tennis score application using Waitress WSGI server."""

# serve.py

import logging
import sys

from waitress import serve

from src.tennis_score.app import app

# Настройка корневого логгера
log_format = '[%(asctime)s] %(levelname)-8s %(name)-25s %(funcName)-25s %(message)s'
log_datefmt = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=log_datefmt,
    handlers=[
        logging.StreamHandler(sys.stdout),  # Вывод в консоль
        logging.FileHandler('tennis_app.log')  # Дополнительно запись в файл
    ]
)
# Явно задаём форматтер для всех обработчиков root-логгера
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    handler.setFormatter(logging.Formatter(log_format, log_datefmt))

# Настройка логгеров для различных модулей
for logger_name in ['controller', 'router', 'app']:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

# Отключим логи от wsgi и настроим уровень для waitress
logging.getLogger('wsgi').setLevel(logging.WARNING)  # Только предупреждения и ошибки
logging.getLogger('waitress').setLevel(logging.INFO)

# Настроим также логи для сервисных слоев, инфраструктуры и репозиториев
logging.getLogger('service').setLevel(logging.DEBUG)
logging.getLogger('repository').setLevel(logging.DEBUG)
logging.getLogger('core').setLevel(logging.DEBUG)


serve(app, host='127.0.0.1', port=8080)

