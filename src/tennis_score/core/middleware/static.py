"""Middleware для обслуживания статических файлов в приложении теннисного скоринга."""

import logging
import mimetypes
import os


class StaticMiddleware:
    """Middleware для обслуживания всех файлов из одной статической директории."""

    def __init__(self, app, static_url='/static/', static_dir='templates/static'):
        """Args:
        app: Оборачиваемое WSGI-приложение
            static_url: URL-префикс, под которым доступны статические файлы
            static_dir: Директория на диске, где хранятся статические файлы.
        """  # noqa: D205
        self.app = app
        self.static_url = static_url.rstrip('/') + '/'
        self.static_dir = static_dir

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')



        if path.startswith(self.static_url):
            relative_path = path[len(self.static_url):].lstrip('/')
            file_path = os.path.join(self.static_dir, relative_path)



            if os.path.isfile(file_path):
                return self.serve_static(file_path, start_response)

        return self.app(environ, start_response)

    def serve_static(self, file_path, start_response):
        """Отдает статический файл клиенту."""
        try:
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'

            file_size = os.path.getsize(file_path)

            headers = [
                ('Content-Type', content_type),
                ('Content-Length', str(file_size)),
                ('Cache-Control', 'public, max-age=86400'),
            ]
            start_response('200 OK', headers)

            with open(file_path, 'rb') as f:
                return [f.read()]

        except Exception as e:
            logging.getLogger("infrastructure.middleware.static").error(
                f"Ошибка при отдаче файла {file_path}: {e}"
            )
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [b'Internal Server Error']
