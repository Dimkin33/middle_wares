"""Controllers for tennis match operations such as creating a new match and updating match scores."""  # noqa: E501

import logging

from ..core.response import make_response
from ..services.match_service import MatchService

# Создаем единый экземпляр сервиса для использования во всех контроллерах
match_service = MatchService()


def new_match_controller(params: dict) -> dict:
    """Контроллер для создания нового матча."""
    logger = logging.getLogger("controller")
    logger.debug(f"new_match_controller: {params}")

    player_one = params.get("playerOne", [""])[0].strip()
    player_two = params.get("playerTwo", [""])[0].strip()

    if not player_one or not player_two:
        return make_response("new-match.html", {"error": "Both player names are required"})

    logger.info(f"New match: {player_one} vs {player_two}")

    # Используем сервис для создания матча
    match_dto = match_service.create_match(player_one, player_two)

    # Получаем данные для отображения
    view_data = match_service.prepare_match_view_data(match_dto)
    # Явно добавляем match_uuid в view_data для использования в шаблоне
    if match_dto:
        view_data["match_uuid"] = match_dto.uuid

    return make_response("match-score.html", view_data)


def match_score_controller(params: dict) -> dict:
    """Контроллер для отображения и обновления счёта матча по UUID."""
    logger = logging.getLogger("controller")
    logger.debug(f"match_score_controller: {params}")

    match_uuid = params.get("match_uuid", [""])[0].strip()
    player_param = params.get("player", [""])[0].strip()

    if not match_uuid:
        logger.warning("match_uuid not provided to match_score_controller")
        # Можно перенаправить на страницу создания нового матча или показать ошибку
        return make_response(
            "new-match.html", {"error": "No match specified. Please start a new match."}
        )

    match_dto = None
    if player_param in ["player1", "player2"]:
        logger.debug(f"Updating score for match {match_uuid}, player {player_param}")
        match_dto = match_service.update_match_score(match_uuid, player_param)
    else:
        logger.debug(f"Fetching score data for match {match_uuid}")
        match_dto = match_service.get_match_data_by_uuid(match_uuid)

    if not match_dto:
        logger.error(f"Failed to get match_dto for UUID {match_uuid} in match_score_controller.")
        # Если матч не найден по UUID, возможно, он был завершен и удален из активных,
        # или UUID некорректен.
        # Можно попытаться загрузить его из истории, если это предусмотрено,
        # или показать ошибку, что матч не найден.
        return make_response(
            "match-score.html",
            {
                "error": f"Match with ID {match_uuid} not found or data is unavailable.",
                "score": {"sets": [0, 0], "games": [0, 0], "points": ["0", "0"]},
                "player_one_name": "N/A",
                "player_two_name": "N/A",
                "match_uuid": match_uuid,  # Возвращаем UUID для контекста
            },
            status="404 Not Found",  # Используем 404, если ресурс не найден
        )

    # Получаем данные для отображения
    view_data = match_service.prepare_match_view_data(match_dto)
    view_data["match_uuid"] = match_dto.uuid # Убедимся, что UUID всегда есть для шаблона

    if match_dto.winner:
        winner_name = match_dto.winner # Если winner это уже имя
        # Если winner это ID, и нужно имя, то потребуется доп. логика или изменение DTO
        view_data["info"] = (
            f"Матч завершён. Победитель: {winner_name}. "
            "Начните новый матч или посмотрите результаты."
        )

    return make_response("match-score.html", view_data)


# def list_matches_controller(params: dict) -> dict:
#     """Контроллер для отображения списка завершенных матчей."""
#     logger = logging.getLogger("controller")
#     logger.debug(f"list_matches_controller: {params}")
#     page = int(params.get("page", ["1"])[0])
#     per_page = 10 # или другое значение по умолчанию

#     matches_dtos, total_pages = match_service.data_handler.list_matches_paginated(page, per_page)
    
#     view_data = {
#         "matches": matches_dtos,
#         "current_page": page,
#         "total_pages": total_pages,
#         "pagination_range": range(1, total_pages + 1)
#     }
#     return make_response("matches.html", view_data)

# def view_match_controller(params: dict) -> dict:
#     """Контроллер для просмотра конкретного завершенного матча по UUID."""
#     logger = logging.getLogger("controller")
#     match_uuid = params.get("match_uuid", [""])[0].strip()
#     if not match_uuid:
#         # Обработка ошибки: UUID не предоставлен
#         return make_response(
#             "matches.html", 
#             {"error": "Match UUID is required.", "matches": [], "total_pages": 0}
#         )
#
#     match_dto = match_service.get_match_data_by_uuid(match_uuid) # Этот метод теперь ищет и в БД
#     if not match_dto:
#         # Обработка ошибки: Матч не найден
#         return make_response(
#             "matches.html", 
#             {"error": f"Match with UUID {match_uuid} not found.", "matches": [], "total_pages": 0}
#         )
#     
#     view_data = match_service.prepare_match_view_data(match_dto)
#     view_data["match_uuid"] = match_dto.uuid
#     view_data["info"] = "Просмотр завершенного матча."
#     return make_response("match-score.html", view_data) # Используем тот же шаблон для отображения
