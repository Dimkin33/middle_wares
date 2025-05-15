"""Инфраструктурный слой приложения теннисного скоринга.

Содержит компоненты, отвечающие за взаимодействие приложения с окружающей средой 
и техническими аспектами реализации: маршрутизация, шаблоны, WSGI-совместимость и т.д.
"""

from .app_orchestrator import AppOrchestrator
from .router import route_request
from .routing import RoutesHandler
from .template import TemplateRenderer

__all__ = [
    "AppOrchestrator",
    "route_request",
    "RoutesHandler",
    "TemplateRenderer",
]
