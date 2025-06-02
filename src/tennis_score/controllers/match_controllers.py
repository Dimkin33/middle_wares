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
        return make_response(
            "new-match.html", {"error": "No match specified. Please start a new match."}
        )

    # Сначала проверяем завершенные матчи в базе данных
    completed_match = match_service.get_completed_match_by_uuid(match_uuid)
    if completed_match:
        logger.info(f"Found completed match {match_uuid} in database")
        
        # Если пользователь пытается обновить счет завершенного матча
        if player_param in ["player1", "player2"]:
            logger.warning(f"Attempt to update completed match {match_uuid}")
            view_data = match_service.prepare_completed_match_view_data(completed_match)
            view_data["error"] = "Этот матч уже завершен. Обновление счета невозможно."
            view_data["match_completed"] = True
            return make_response("match-score.html", view_data)
        
        # Просто отображаем завершенный матч
        view_data = match_service.prepare_completed_match_view_data(completed_match)
        view_data["match_completed"] = True
        return make_response("match-score.html", view_data)

    # Обработка активных матчей
    match_dto = None
    if player_param in ["player1", "player2"]:
        logger.debug(f"Updating score for match {match_uuid}, player {player_param}")
        match_dto = match_service.update_match_score(match_uuid, player_param)
    else:
        logger.debug(f"Fetching score data for match {match_uuid}")
        match_dto = match_service.get_match_data_by_uuid(match_uuid)

    if not match_dto:
        logger.error(f"Match {match_uuid} not found in active matches or database")
        return make_response(
            "error.html",
            {
                "error_title": "Матч не найден",
                "error_message": f"Матч с ID {match_uuid} не найден или недоступен.",
                "error_details": "Возможно, матч был завершен или удален. Попробуйте начать новый матч.",
                "show_new_match_button": True
            },
            status="404 Not Found"
        )

    # Получаем данные для отображения активного матча
    view_data = match_service.prepare_match_view_data(match_dto)
    view_data["match_uuid"] = match_dto.uuid
    view_data["match_completed"] = False

    # Проверяем, не завершился ли матч после последнего обновления
    if match_dto.winner:
        view_data["match_completed"] = True
        view_data["info"] = (
            f"🎉 Матч завершён! Победитель: {match_dto.winner}. "
            "Поздравляем! Вы можете начать новый матч."
        )

    return make_response("match-score.html", view_data)

def reset_match_controller(params: dict) -> dict:
    """Контроллер для сброса счета матча по UUID.

    Args:
        params: параметры запроса, должен содержать 'match_uuid'

    Returns:
        dict: ответ с данными для шаблона match-score.html или error.html
    """
    logger = logging.getLogger("controller.reset")
    logger.debug(f"Processing reset_match request with params: {params}")

    match_uuid = params.get("match_uuid", [""])[0].strip()
    
    if not match_uuid:
        logger.warning("match_uuid not provided to reset_match_controller")
        return make_response(
            "new-match.html", 
            {"error": "Match UUID is required to reset. Please start a new match."}
        )

    # Проверяем, не завершен ли матч
    completed_match = match_service.get_completed_match_by_uuid(match_uuid)
    if completed_match:
        logger.warning(f"Attempt to reset completed match {match_uuid}")
        return make_response(
            "error.html",
            {
                "error_title": "Невозможно сбросить матч",
                "error_message": "Этот матч уже завершен и не может быть сброшен.",
                "error_details": f"Матч завершился. Победитель: {completed_match.get('winner', 'N/A')}.",
                "show_new_match_button": True
            },
            status="400 Bad Request"
        )

    # Пытаемся сбросить активный матч
    try:
        match_service.reset_match_score(match_uuid)
        logger.info(f"Match {match_uuid} has been reset")
    except Exception as e:
        logger.error(f"Failed to reset match {match_uuid}: {e}")
        return make_response(
            "error.html",
            {
                "error_title": "Ошибка сброса матча",
                "error_message": f"Не удалось сбросить матч {match_uuid}.",
                "error_details": "Возможно, матч не найден или произошла техническая ошибка.",
                "show_new_match_button": True
            },
            status="500 Internal Server Error"
        )

    # Получаем обновленные данные матча
    match_dto = match_service.get_match_data_by_uuid(match_uuid)

    if not match_dto:
        logger.error(f"Failed to get match_dto for UUID {match_uuid} after reset.")
        return make_response(
            "error.html",
            {
                "error_title": "Ошибка получения данных",
                "error_message": f"Не удалось получить данные матча {match_uuid} после сброса.",
                "error_details": "Матч был сброшен, но возникла проблема с получением данных.",
                "show_new_match_button": True
            },
            status="500 Internal Server Error"
        )

    view_data = match_service.prepare_match_view_data(match_dto)
    view_data["match_uuid"] = match_uuid
    view_data["match_completed"] = False
    view_data["info"] = "✅ Счет матча был успешно сброшен. Игра может продолжаться!"

    return make_response("match-score.html", view_data)
