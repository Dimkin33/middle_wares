"""Middleware for logging HTTP requests and responses in the tennis_score application."""

import logging
import time


# middlewares/logging.py
class LoggingMiddleware:
    """WSGI middleware for logging HTTP requests and responses."""

    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("wsgi")

        # Пути, для которых не нужно детальное логирование
        self.skip_detailed_logging_paths = ["/css/", "/js/", "/images/"]

    def should_log_detailed(self, path):
        """Проверяет, нужно ли детально логировать запрос по данному пути."""
        return not any(path.startswith(skip_path) for skip_path in self.skip_detailed_logging_paths)

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "-")
        method = environ.get("REQUEST_METHOD", "-")

        # Детальное логирование только для важных запросов
        detailed_logging = self.should_log_detailed(path)

        if detailed_logging:
            query_string = environ.get("QUERY_STRING", "")
            client_addr = environ.get("REMOTE_ADDR", "-")

            # Логируем детали запроса
            self.logger.info(
                f"Request: {method} {path}{' ?' + query_string if query_string else ''} from {client_addr}"
            )

            # Замеряем время выполнения запроса
            start_time = time.time()

        # Перехватываем результаты start_response для важных запросов
        if detailed_logging:

            def custom_start_response(status, headers, exc_info=None):
                self.logger.info(f"Response: {status}")
                return start_response(status, headers, exc_info)

            wrapped_start_response = custom_start_response
        else:
            wrapped_start_response = start_response

        # Выполняем запрос и получаем результат
        result = self.app(environ, wrapped_start_response)

        # Логируем время выполнения для важных запросов
        if detailed_logging:
            end_time = time.time()
            self.logger.info(f"Request completed in {end_time - start_time:.6f}s")

        return result
