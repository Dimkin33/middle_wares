# filepath: c:\Users\dimki\Project\middle_wares\src\tennis_score\app.py
"""Модуль app.

Входная точка WSGI-приложения для теннисного скоринга.
"""

import logging
import sys

from .services.app_orchestrator import AppOrchestrator

# Настройка логгера при запуске модуля напрямую (не через импорт)
if __name__ == "__main__":
    logging.basicConfig(
        filename="tennis_app.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)

# Создание и настройка приложения с использованием оркестратора
app_orchestrator = AppOrchestrator()
app = app_orchestrator.create_app()

# Запуск встроенного сервера при непосредственном вызове скрипта
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    
    port = 8000
    logging.info(f"Starting server on port {port}...")
    with make_server("", port, app) as httpd:
        logging.info(f"Server is running on port {port}")
        httpd.serve_forever()
