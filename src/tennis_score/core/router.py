"""Маршрутизация для веб-приложения теннисного скоринга (объединённый router)."""

import logging
from urllib.parse import parse_qs

from ..controllers.list_controllers import list_matches_controller
from ..controllers.match_controllers import (
    match_score_controller,
    new_match_controller,
    reset_match_controller,
)
from ..controllers.view_controllers import TemplateViewController
from .response import make_response


class RoutesHandler:
    """Обработчик маршрутов для управления роутингом HTTP запросов."""
    def __init__(self, routing_table: dict):
        self.routing_table = routing_table
        self.logger = logging.getLogger("core.routing")

    def route_request(self, path: str, method: str, environ: dict | None = None) -> dict:
        self.logger.info(f"route_request: {method} {path}")
        
        # Отделяем путь от строки запроса для точного совпадения маршрута
        actual_path = path.split('?')[0]
        
        controller = self.routing_table.get((actual_path, method))
        if not controller:
            self.logger.warning(f"Route not found: {method} {actual_path}")
            return make_response(None, {}, status="404 Not Found")
        self.logger.debug(f"Matched route: {method} {actual_path}")
        
        params = {}
        if environ: # environ должен быть всегда доступен
            if method == "POST":
                params = self._parse_post_data(environ)
                self.logger.debug(f"POST params: {params}")
            elif method == "GET":
                query_string = environ.get("QUERY_STRING", "")
                if query_string:
                    params = parse_qs(query_string)
                    self.logger.debug(f"GET query params: {params}")
        
        return controller(params)

    @staticmethod
    def _parse_post_data(environ: dict) -> dict:
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            size = 0
        body = environ.get("wsgi.input")
        body_bytes = body.read(size) if body and size > 0 else b""
        return parse_qs(body_bytes.decode("utf-8"))

# Определение маршрутов приложения
ROUTING_TABLE: dict[tuple[str, str], callable] = {
    ("/", "GET"): TemplateViewController("index.html"),
    ("/new-match", "GET"): TemplateViewController("new-match.html"),
    ("/new-match", "POST"): new_match_controller,
    ("/match-score", "GET"): match_score_controller, # Изменено для динамического отображения
    ("/match-score", "POST"): match_score_controller,
    ("/matches", "GET"): list_matches_controller,
    ("/reset-match", "POST"): reset_match_controller,
}

routes_handler = RoutesHandler(ROUTING_TABLE)

def route_request(path: str, method: str, environ: dict | None = None) -> dict:
    """Маршрутизация HTTP запросов к соответствующим контроллерам."""
    logger = logging.getLogger("router")
    logger.debug(f"Routing request: {method} {path}")
    return routes_handler.route_request(path, method, environ)
