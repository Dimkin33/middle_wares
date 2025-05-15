"""Маршрутизатор для теннисного приложения."""
import logging

from ..controllers.list_controllers import list_matches_controller, reset_match_controller
from ..controllers.match_controllers import match_score_controller, new_match_controller
from ..controllers.view_controllers import TemplateViewController
from .routing import RoutesHandler

# Определение маршрутов приложения
ROUTING_TABLE: dict[tuple[str, str], callable] = {
    # Основные страницы
    ("/", "GET"): TemplateViewController("index.html"),
    ("/new-match", "GET"): TemplateViewController("new-match.html"),
    ("/new-match", "POST"): new_match_controller,
    
    # Страницы матчей
    ("/match-score", "GET"): TemplateViewController("match-score.html"),
    ("/match-score", "POST"): match_score_controller,
    
    # Управление матчами
    ("/matches", "GET"): list_matches_controller,
    ("/reset-match", "POST"): reset_match_controller,
}

# Создаем экземпляр обработчика маршрутов
routes_handler = RoutesHandler(ROUTING_TABLE)

def route_request(path: str, method: str, environ: dict | None = None) -> dict:
    """Универсальная маршрутизация GET/POST запросов.
    
    Args:
        path: путь запроса
        method: HTTP метод (GET, POST)
        environ: WSGI окружение
        
    Returns:
        dict: результат выполнения контроллера
    """
    logger = logging.getLogger("router")
    logger.debug(f"Routing request: {method} {path}")
    
    # Делегируем обработку маршрута обработчику маршрутов
    return routes_handler.route_request(path, method, environ)
