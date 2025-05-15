# app.py
"""Модуль app.

Содержит функции и классы для работы с теннисным скорингом.
"""

import logging
import os
from collections.abc import Callable, Iterable
from typing import TypeAlias

from jinja2 import Environment, FileSystemLoader

from src.tennis_score.middlewares.cors import CORSMiddleware
from src.tennis_score.middlewares.logging import LoggingMiddleware
from src.tennis_score.middlewares.static import StaticMiddleware
from src.tennis_score.router import route_request

Headers: TypeAlias = list[tuple[str, str]]

# Настройка Jinja2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")  # Исправляем путь
env = Environment(loader=FileSystemLoader(templates_dir))


def render_template(template_name: str, **context: dict[str, object]) -> bytes:
    """Отрендерить шаблон с заданным контекстом.

    Args:
        template_name: Имя шаблона для рендеринга
        context: Контекст для шаблона (переменные)

    Returns:
        Байтовая строка с HTML-кодом
    """
    template = env.get_template(template_name)
    return template.render(**context).encode("utf-8")


def app(
    environ: dict[str, object], 
    start_response: Callable[[str, Headers], None]
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

    # Передаем environ в router для обработки POST-данных
    route: dict[str, object] = route_request(path, method, environ=environ)
    logging.getLogger("app").debug(f"route: {route}")
    # Если route не None, то рендерим шаблон
    if route and route["template"]:
        content: bytes = render_template(route["template"], **route["context"])
        status: str = route["status"]
        headers: Headers = route["headers"]
    else:
        content = b"<h1>404 Not Found</h1>"
        status = "404 Not Found"
        headers = [("Content-Type", "text/html; charset=utf-8")]

    start_response(status, headers)
    return [content]


# StaticMiddleware ищет статику в папках css, js, images внутри templates по корню '/'
static_dirs: list[str] = [
    os.path.join(templates_dir, "css"),
    os.path.join(templates_dir, "js"),
    os.path.join(templates_dir, "images"),
]

# Оборачиваем в миддлвары
app = StaticMiddleware(app, static_root="/", static_dirs=static_dirs)
app = CORSMiddleware(app)
app = LoggingMiddleware(app)
