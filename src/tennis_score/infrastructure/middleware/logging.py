"""Middleware для логирования HTTP-запросов и ответов в приложении теннисного скоринга."""

import logging
import time


class LoggingMiddleware:
    """WSGI middleware для логирования HTTP-запросов и ответов."""

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
            user_agent = environ.get("HTTP_USER_AGENT", "-")
            
            self.logger.info(
                f"Request: {method} {path}?{query_string} from {client_addr} "
                f"with {user_agent}"
            )
        
        start_time = time.time()

        # Создаем обертку для start_response для захвата статуса ответа
        def custom_start_response(status, headers, exc_info=None):
            if detailed_logging:
                self.logger.debug(f"Response status: {status}")
                for h, v in headers:
                    self.logger.debug(f"Response header: {h}: {v}")
            return start_response(status, headers, exc_info)
        
        # Вызываем приложение
        response = self.app(environ, custom_start_response)
        
        # Измеряем время выполнения запроса
        end_time = time.time()
        process_time = end_time - start_time
        
        if detailed_logging:
            self.logger.info(f"Request {method} {path} processed in {process_time:.4f}s")
        else:
            self.logger.debug(f"Request {method} {path} processed in {process_time:.4f}s")
        
        return response
