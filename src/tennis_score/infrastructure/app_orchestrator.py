"""Оркестратор WSGI-приложения для теннисного скоринга."""

import logging
import os
from collections.abc import Callable, Iterable
from typing import TypeAlias

from ..middlewares.cors import CORSMiddleware
from ..middlewares.logging import LoggingMiddleware
from ..middlewares.static import StaticMiddleware
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
        """Создает WSGI-приложение с необходимыми middleware.
        
        Returns:
            Callable: WSGI-совместимая функция приложения
        """
        app = self.wsgi_app
        
        # Настраиваем статические директории
        static_dirs: list[str] = [
            os.path.join(self.templates_dir, "css"),
            os.path.join(self.templates_dir, "js"),
            os.path.join(self.templates_dir, "images"),
        ]
        
        # Оборачиваем в миддлвары
        app = StaticMiddleware(app, static_root="/", static_dirs=static_dirs)
        app = CORSMiddleware(app)
        app = LoggingMiddleware(app)
        
        self.logger.info("Application created with all middleware")
        return app
