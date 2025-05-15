"""Обработчик маршрутов для приложения теннисного скоринга."""

import logging
from urllib.parse import parse_qs

from ..utils import make_response


class RoutesHandler:
    """Обработчик маршрутов для управления роутингом запросов."""

    def __init__(self, routing_table: dict):
        """Инициализация обработчика маршрутов.
        
        Args:
            routing_table: словарь маршрутов в формате {(путь, метод): контроллер}
        """
        self.routing_table = routing_table
        self.logger = logging.getLogger("service.routes")

    def route_request(self, path: str, method: str, environ: dict | None = None) -> dict:
        """Универсальная маршрутизация GET/POST запросов.
        
        Args:
            path: путь запроса
            method: HTTP метод (GET, POST)
            environ: WSGI окружение
            
        Returns:
            dict: результат выполнения контроллера
        """
        self.logger.info(f"route_request: {method} {path}")

        controller = self.routing_table.get((path, method))
        if not controller:
            self.logger.warning(f"Route not found: {method} {path}")
            return make_response(None, {}, status="404 Not Found")

        self.logger.debug(f"Matched route: {method} {path}")

        # Определяем параметры запроса
        params = {}
        if method == "POST" and environ:
            params = self._parse_post_data(environ)
            self.logger.debug(f"POST params: {params}")

        # Вызываем соответствующий контроллер
        return controller(params)

    @staticmethod
    def _parse_post_data(environ: dict) -> dict:
        """Чтение данных из POST-запроса.
        
        Args:
            environ: WSGI окружение
            
        Returns:
            dict: параметры из тела POST-запроса
        """
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            size = 0

        body = environ.get("wsgi.input")
        body_bytes = body.read(size) if body and size > 0 else b""

        return parse_qs(body_bytes.decode("utf-8"))
