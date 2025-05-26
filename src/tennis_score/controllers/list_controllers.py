# filepath: c:\Users\dimki\Project\middle_wares\src\tennis_score\controllers\list_controllers.py
"""Контроллеры для отображения списка матчей и связанных операций."""

import logging

from ..core.response import make_response
from .match_controllers import match_service


def list_matches_controller(params: dict) -> dict:
    """Контроллер для отображения списка матчей с пагинацией."""
    logger = logging.getLogger("controller.list")
    logger.debug(f"Processing list_matches request with params: {params}")

    # Получаем параметры пагинации из params (например, ?page=2)
    # page = int(params.get("page", [1])[0]) if "page" in params else 1 # Старая версия
    page = 1  # Значение по умолчанию для страницы
    page_param_list = params.get("page")
    if page_param_list:
        try:
            page_val = int(page_param_list[0])
            if page_val >= 1:
                page = page_val
            else:
                logger.warning(f"Page number {page_val} is less than 1. Using page 1.")
                # page остается 1
        except ValueError:
            logger.warning(f"Invalid page parameter: '{page_param_list[0]}'. Using page 1.")
            # page остается 1
    else:
        logger.debug("Page parameter not found. Using page 1.")

    per_page = 4  # Можно сделать настраиваемым
    logger.debug(f"Requesting matches for page: {page}, per_page: {per_page}")

    # Получаем список матчей и общее количество страниц через сервис
    matches, total_pages = match_service.data_handler.list_matches_paginated(page, per_page)

    # Возвращаем контекст с данными о матчах и параметрами пагинации
    return make_response(
        "matches.html",
        {
            "matches": matches,
            "page": page,
            "total_pages": total_pages,
        },
    )


def reset_match_controller(params: dict) -> dict:
    """Контроллер для сброса счета матча по UUID.

    Args:
        params: параметры запроса, должен содержать 'match_uuid'

    Returns:
        dict: ответ с данными для шаблона match-score.html
    """
    logger = logging.getLogger("controller.reset")
    logger.debug(f"Processing reset_match request with params: {params}")

    match_uuid = params.get("match_uuid", [""])[0].strip()

    if not match_uuid:
        logger.warning("match_uuid not provided to reset_match_controller")
        # Возвращаем на страницу нового матча с ошибкой
        return make_response(
            "new-match.html", {"error": "Match UUID is required to reset. Please start a new match."}
        )

    # Сбрасываем счет матча через сервис, используя UUID
    match_service.reset_match_score(match_uuid)
    logger.info(f"Match {match_uuid} has been reset")

    # После сброса получаем обновленные данные матча по UUID
    match_dto = match_service.get_match_data_by_uuid(match_uuid)

    if not match_dto:
        logger.error(f"Failed to get match_dto for UUID {match_uuid} after reset.")
        return make_response(
            "match-score.html",
            {
                "error": f"Could not retrieve data for match {match_uuid} after reset.",
                "match_uuid": match_uuid,
            },
            status="404 Not Found",
        )

    # Подготавливаем данные для отображения
    # prepare_match_view_data теперь получает всю необходимую информацию из DTO
    view_data = match_service.prepare_match_view_data(match_dto)
    view_data["match_uuid"] = match_uuid  # Убедимся, что UUID есть для шаблона
    view_data["info"] = f"Счет матча {match_uuid} был сброшен."

    return make_response("match-score.html", view_data)
