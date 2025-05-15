# src/middle_wares/middlewares/static.py

"""Модуль static.

Содержит функции и классы для работы с теннисным скорингом.
"""

import mimetypes
import os


class StaticMiddleware:
    """Класс StaticMiddleware.
    
    Отвечает за функциональность, связанную с StaticMiddleware.
    """
    def __init__(self, app, static_root="/", static_dirs=None):
        """Инициализирует объект класса.
        
        Args:
            app: WSGI приложение, которое будет обернуто
            static_root: Корневой путь для статических файлов
            static_dirs: Список директорий со статическими файлами
        """
        self.app = app
        self.static_root = static_root
        if static_dirs is None:
            static_dirs = []
        self.static_dirs = static_dirs

    def __call__(self, environ, start_response):
        """Обрабатывает WSGI вызов и обслуживает статические файлы.
        
        Args:
            environ: Окружение WSGI с информацией о запросе
            start_response: Функция для инициализации ответа
            
        Returns:
            Итерируемый объект с байтовым содержимым ответа
        """
        path = environ.get("PATH_INFO", "")
        rel_path = path[1:] if path.startswith("/") else path
        for static_dir in self.static_dirs:
            prefix = os.path.basename(static_dir) + "/"
            if rel_path.startswith(prefix):
                file_path = os.path.join(static_dir, rel_path[len(prefix) :])
                if os.path.isfile(file_path):
                    content_type, _ = mimetypes.guess_type(file_path)
                    content_type = content_type or "application/octet-stream"
                    with open(file_path, "rb") as f:
                        content = f.read()
                    start_response("200 OK", [("Content-Type", content_type)])
                    return [content]
        return self.app(environ, start_response)
