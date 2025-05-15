"""Маршрутизатор для теннисного приложения.

Этот модуль реэкспортирует функциональность из infrastructure.router для обратной совместимости.
В новом коде рекомендуется использовать напрямую tennis_score.infrastructure.router.
"""

from .infrastructure.router import ROUTING_TABLE, route_request, routes_handler

__all__ = ["ROUTING_TABLE", "route_request", "routes_handler"]
