"""Модуль app.

Входная точка WSGI-приложения для теннисного скоринга.
"""

import logging

from .core.app_orchestrator import AppOrchestrator

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
