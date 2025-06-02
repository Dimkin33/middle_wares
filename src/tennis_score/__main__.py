"""Главный модуль для запуска теннисного приложения."""

import logging
import os
import sys
from wsgiref.simple_server import make_server

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.tennis_score.core.app_orchestrator import AppOrchestrator


def main():
    """Главная функция для запуска приложения."""
    # Создание и настройка приложения с использованием оркестратора
    app_orchestrator = AppOrchestrator()
    app = app_orchestrator.create_app()
    
    port = 8000
    logging.info(f"Starting tennis server on port {port}...")
    
    try:
        with make_server("", port, app) as httpd:
            logging.info(f"Tennis server is running on http://localhost:{port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")

if __name__ == "__main__":
    main()
