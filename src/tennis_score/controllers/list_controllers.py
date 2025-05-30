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
    filter_query_list = params.get("filter_query")
    filter_query = filter_query_list[0] if filter_query_list and filter_query_list[0].strip() else None
    if filter_query:
        logger.debug(f"Applying filter: '{filter_query}'")
    
    logger.debug(f"Requesting matches for page: {page}, per_page: {per_page}, filter: '{filter_query}'")

    # Получаем список матчей и общее количество страниц через сервис
    matches, total_pages = match_service.data_handler.list_matches_paginated(page, per_page, filter_query)

    # Возвращаем контекст с данными о матчах и параметрами пагинации
    return make_response(
        "matches.html",
        {
            "matches": matches,
            "page": page,
            "total_pages": total_pages,
            "filter_query": filter_query if filter_query else "", # Для отображения в поле ввода
        },
    )


# Контроллер reset_match_controller будет перемещен в match_controllers.py
