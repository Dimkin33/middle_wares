"""Инфраструктурный слой приложения теннисного скоринга.

Содержит компоненты, отвечающие за взаимодействие приложения с окружающей средой 
и техническими аспектами реализации: маршрутизация, шаблоны, WSGI-совместимость и т.д.
"""

# Важно: импортируем только те компоненты, которые не создадут циклических зависимостей
from .middleware import CORSMiddleware, LoggingMiddleware, StaticMiddleware
from .template import TemplateRenderer

# Убираем импорт response.make_response из __init__.py для избежания циклических зависимостей
# Экспортируем саму функцию для обратной совместимости
__all__ = [
    "CORSMiddleware",
    "LoggingMiddleware",
    "StaticMiddleware",
    "TemplateRenderer",
]

# Следующие импорты могут создавать циклические зависимости, поэтому делаем их
# доступными, но не загружаем сразу
from .app_orchestrator import AppOrchestrator
from .router import route_request
from .routing import RoutesHandler

__all__ += [
    "AppOrchestrator",
    "route_request",
    "RoutesHandler",
]
