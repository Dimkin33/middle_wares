"""Компоненты для формирования HTTP-ответов."""


def make_response(
    template: str | None, context: dict | None = None, status: str = "200 OK"
) -> dict:
    """Создание ответа для рендеринга в шаблонизаторе.

    Args:
        template: Имя HTML-шаблона для рендеринга
        context: Данные для шаблона
        status: HTTP-статус ответа

    Returns:
        Словарь, содержащий информацию для рендеринга HTTP-ответа
    """
    return {
        "template": template,
        "context": context or {},
        "status": status,
        "headers": [("Content-Type", "text/html; charset=utf-8")],
    }
