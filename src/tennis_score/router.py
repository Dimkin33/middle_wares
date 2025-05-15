import logging  # noqa: D100
from urllib.parse import parse_qs

from .controllers.match_controllers import match_score_controller, new_match_controller
from .controllers.view_controllers import TemplateViewController
from .utils import make_response

ROUTING_TABLE: dict[tuple[str, str], callable] = {
    ("/", "GET"): TemplateViewController("index.html"),
    ("/new-match", "GET"): TemplateViewController("new-match.html"),
    ("/new-match", "POST"): new_match_controller,
    ("/match-score", "GET"): TemplateViewController("match-score.html"),
    ("/match-score", "POST"): match_score_controller,
}


def route_request(path: str, method: str, environ: dict | None = None) -> dict:
    """Универсальная маршрутизация GET/POST запросов."""
    logger = logging.getLogger("router")
    logger.info(f"route_request: {method} {path}")

    controller = ROUTING_TABLE.get((path, method))
    if not controller:
        return make_response(None, {}, status="404 Not Found")

    logger.debug(f"Matched route: {method} {path}")

    # Определяем параметры запроса
    params = {}
    if method == "POST" and environ:
        params = _parse_post_data(environ)

    return controller(params)


def _parse_post_data(environ: dict) -> dict:
    """Чтение данных из POST-запроса."""
    try:
        size = int(environ.get("CONTENT_LENGTH", 0))
    except (ValueError, TypeError):
        size = 0

    body = environ.get("wsgi.input")
    body_bytes = body.read(size) if body and size > 0 else b""

    return parse_qs(body_bytes.decode("utf-8"))


# Функция make_response перенесена в utils.py
