"""Инфраструктурный слой приложения теннисного скоринга.

Содержит компоненты, отвечающие за взаимодействие приложения с окружающей средой 
и техническими аспектами реализации: маршрутизация, шаблоны, WSGI-совместимость и т.д.
"""

# Импорт middleware для обработки CORS, логирования и статики
# Импорт оркестратора приложения (создание WSGI-приложения)
from .app_orchestrator import AppOrchestrator
from .middleware import CORSMiddleware, LoggingMiddleware, StaticMiddleware

# Импорт маршрутизатора и функции маршрутизации
from .router import RoutesHandler, route_request

# Импорт шаблонизатора
from .template import TemplateRenderer

__all__ = [
    "CORSMiddleware",      # Middleware для CORS
    "LoggingMiddleware",   # Middleware для логирования
    "StaticMiddleware",    # Middleware для отдачи статики
    "TemplateRenderer",    # Рендеринг HTML-шаблонов
    "AppOrchestrator",     # Оркестратор WSGI-приложения
    "route_request",       # Универсальная функция маршрутизации
    "RoutesHandler",       # Класс-обработчик маршрутов
]
