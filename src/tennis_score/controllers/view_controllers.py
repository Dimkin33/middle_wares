"""View controllers for rendering templates in tennis_score application."""

import logging

from ..core.response import make_response


class TemplateViewController:
    """Контроллер для простых GET-запросов, возвращающих шаблоны.
    Позволяет стандартизировать обработку запросов.
    """  # noqa: D205

    def __init__(self, template_name: str, default_context: dict = None):
        self.template_name = template_name
        self.default_context = default_context or {}
        self.logger = logging.getLogger("controller.template")

    def __call__(self, params: dict = None) -> dict:
        """Обрабатывает запрос и возвращает ответ с шаблоном.

        Args:
            params: Параметры запроса (для совместимости с другими контроллерами)

        Returns:
            Ответ с шаблоном
        """
        self.logger.debug(f"Rendering template: {self.template_name}")
        return make_response(self.template_name, self.default_context)
