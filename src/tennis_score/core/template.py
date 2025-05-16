"""Сервисы для рендеринга шаблонов."""

import logging
import os

from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    """Класс для рендеринга HTML шаблонов с использованием Jinja2."""

    def __init__(self, templates_dir=None):
        """Инициализирует объект класса.
        
        Args:
            templates_dir: директория с шаблонами. Если None, используется ../templates
        """
        self.logger = logging.getLogger("core.template")
        
        if templates_dir is None:
            # Определяем путь к шаблонам относительно текущего файла
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            templates_dir = os.path.join(base_dir, "templates")
        
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.logger.debug(f"Template renderer initialized with dir: {templates_dir}")

    def render(self, template_name: str, context: dict = None) -> bytes:
        """Отрендерить шаблон с заданным контекстом.

        Args:
            template_name: Имя шаблона для рендеринга (относительно templates_dir)
            context: Контекст для шаблона (переменные)

        Returns:
            Байтовая строка с HTML-кодом
        """
        if context is None:
            context = {}
            
        self.logger.debug(f"Rendering template: {template_name}")
        template = self.env.get_template(template_name)
        
        try:
            html_content = template.render(**context)
            return html_content.encode()
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {e}")
            return f"<h1>Error rendering template</h1><p>{str(e)}</p>".encode()
