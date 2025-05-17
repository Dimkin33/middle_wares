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
    view_data = match_service.prepare_match_view_data(match_dto, player_one, player_two)

    return make_response("match-score.html", view_data)


def match_score_controller(params: dict) -> dict:
    """Контроллер для обновления счёта матча."""
    logger = logging.getLogger("controller")
    logger.debug(f"match_score_controller: {params}")

    # Проверяем наличие текущего матча
    current_match = match_service.repository.get_current_match()

    if not current_match:
        # Если нет активного матча, но есть завершённые — показываем последний завершённый
        finished_matches = match_service.repository.finished_matches
        if finished_matches:
            last_match = finished_matches[-1]
            match_dto = last_match.get_match_data()
            p1_name = getattr(last_match, "player_one_name", "")
            p2_name = getattr(last_match, "player_two_name", "")
            view_data = match_service.prepare_match_view_data(match_dto, p1_name, p2_name)
            view_data["info"] = "Матч завершён. Начните новый матч или посмотрите результаты."
            return make_response("match-score.html", view_data)
        logger.error("No active match found.")
        return make_response(
            "match-score.html",
            {
                "error": "No active match found",
                "score": {"sets": [0, 0], "games": [0, 0], "points": ["0", "0"]},
                "player_one_name": "",
                "player_two_name": "",
            },
            status="400 Bad Request",
        )

    player_param = params.get("player", [""])[0]

    match_dto = None
    if player_param in ["player1", "player2"]:
        # Используем сервис для обновления счета
        match_dto = match_service.update_current_match_score(player_param)
    else:
        # Используем сервис для получения текущих данных матча
        match_dto = match_service.get_current_match_data()

    if not match_dto:
        logger.error("Failed to get match_dto in match_score_controller.")
        return make_response(
            "match-score.html",
            {
                "error": "Match data is unavailable.",
                "score": {"sets": [0, 0], "games": [0, 0], "points": ["0", "0"]},
                "player_one_name": "",
                "player_two_name": "",
            },
            status="500 Internal Server Error",
        )

    # Получаем имена игроков из текущего матча
    if current_match:
        p1_name = getattr(current_match, "player_one_name", "")
        p2_name = getattr(current_match, "player_two_name", "")
    else:
        p1_name = getattr(match_dto, "player1", "")
        p2_name = getattr(match_dto, "player2", "")

    # Получаем данные для отображения
    view_data = match_service.prepare_match_view_data(match_dto, p1_name, p2_name)

    return make_response("match-score.html", view_data)
