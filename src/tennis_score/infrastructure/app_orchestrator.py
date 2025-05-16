"""Оркестратор WSGI-приложения для теннисного скоринга."""

import logging
import os
from collections.abc import Callable, Iterable
from typing import TypeAlias

from .middleware import CORSMiddleware, LoggingMiddleware, StaticMiddleware
from .router import route_request
from .template import TemplateRenderer

Headers: TypeAlias = list[tuple[str, str]]

class AppOrchestrator:
    """Оркестратор приложения, отвечающий за настройку и запуск WSGI-сервера."""

    def __init__(self):
        """Инициализирует объект класса."""
        self.logger = logging.getLogger("infrastructure.app")
        
        # Определяем базовую директорию приложения
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.templates_dir = os.path.join(self.base_dir, "templates")
        
        # Инициализируем рендерер шаблонов
        self.template_renderer = TemplateRenderer(self.templates_dir)
        self.logger.debug("AppOrchestrator initialized")

    def wsgi_app(
        self, environ: dict[str, object], start_response: Callable[[str, Headers], None]
    ) -> Iterable[bytes]:
        """Основная WSGI-функция приложения.
        
        Обрабатывает запросы, маршрутизирует их и возвращает ответ.
        
        Args:
            environ: Окружение WSGI с информацией о запросе
            start_response: Функция для инициализации ответа
            
        Returns:
            Итерируемый объект с байтовым содержимым ответа
        """
        path: str = environ.get("PATH_INFO", "/")
        method: str = environ.get("REQUEST_METHOD", "GET")
        
        # Логируем каждый запрос
        self.logger.info(f"Request: {method} {path}")

        # Передаем environ в router для обработки POST-данных
        route: dict[str, object] = route_request(path, method, environ=environ)
        
        # Если route не None и шаблон определен, рендерим шаблон
        if route and route["template"]:
            content: bytes = self.template_renderer.render(
                route["template"], route["context"]
            )
            status: str = route["status"]
            headers: Headers = route["headers"]
        else:
            content = b"<h1>404 Not Found</h1>"
            status = "404 Not Found"
            headers = [("Content-Type", "text/html; charset=utf-8")]

        self.logger.debug(f"Response: {status}")
        start_response(status, headers)
        return [content]

    def create_app(self):
        """Создает WSGI-приложение с необходимыми middleware."""
        app = self.wsgi_app

        # Путь к общей директории со статическими файлами
        static_dir = os.path.join(self.templates_dir, "static")

        # Проверим существование директории
        if os.path.exists(static_dir):
            self.logger.debug(f"Статическая директория: {static_dir}")
            for root, dirs, files in os.walk(static_dir):
                rel_root = os.path.relpath(root, static_dir)
                self.logger.debug(f"  [{rel_root}] → {files}")
        else:
            self.logger.warning(f"Статическая директория не найдена: {static_dir}")

        # Используем упрощённую StaticMiddleware (новую версию!)
        app = StaticMiddleware(
            app,
            static_url='/static/',
            static_dir=static_dir
        )
        app = CORSMiddleware(app)
        app = LoggingMiddleware(app)

        self.logger.info("WSGI-приложение собрано с middleware")
        return app

