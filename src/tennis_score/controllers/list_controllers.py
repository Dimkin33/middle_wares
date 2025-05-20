# filepath: c:\Users\dimki\Project\middle_wares\src\tennis_score\controllers\list_controllers.py
"""Контроллеры для отображения списка матчей и связанных операций."""

import logging

from ..core.response import make_response
from .match_controllers import match_service


def list_matches_controller(params: dict) -> dict:
    """Контроллер для отображения списка матчей с пагинацией."""
    logger = logging.getLogger("controller.list")
    logger.debug("Processing list_matches request")

    # Получаем параметры пагинации из params (например, ?page=2)
    page = int(params.get("page", [1])[0]) if "page" in params else 1
    per_page = 4  # Можно сделать настраиваемым

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
    """Контроллер для сброса текущего матча.
    
    Args:
        params: параметры запроса
        
    Returns:
        dict: ответ с перенаправлением
    """
    logger = logging.getLogger("controller.reset")
    logger.debug("Processing reset_match request")
    
    # Сбрасываем счет текущего матча через сервис
    match_service.reset_current_match()
    logger.info("Match has been reset")
    
    # После сброса получаем обновленные данные матча
    match_dto = match_service.get_current_match_data()
    
    # Получаем имена игроков из текущего матча
    current_match = match_service.repository.get_current_match()
    p1_name = getattr(current_match, "player_one_name", "")
    p2_name = getattr(current_match, "player_two_name", "")
    
    # Подготавливаем данные для отображения
    view_data = match_service.prepare_match_view_data(match_dto, p1_name, p2_name)
    
    return make_response("match-score.html", view_data)
