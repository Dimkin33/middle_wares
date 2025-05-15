"""Обработчик данных для отображения матча.

Этот модуль отвечает за подготовку данных для отображения на веб-страницах.
"""
import json
import logging


class ViewDataHandler:
    """Класс для подготовки данных о матче для отображения."""

    def __init__(self, repository):
        """Инициализация обработчика данных для представления.
        
        Args:
            repository: репозиторий для доступа к данным матчей
        """
        self.logger = logging.getLogger("service.view")
        self.repository = repository

    def prepare_match_view_data(self, match_dto, player_one_name_arg=None, player_two_name_arg=None):
        """Подготовка данных для отображения матча.
        
        Args:
            match_dto: DTO матча или None
            player_one_name_arg: имя первого игрока (если передано)
            player_two_name_arg: имя второго игрока (если передано)
            
        Returns:
            dict: контекст для отображения матча в шаблонизаторе
        """
        # Добавляем логирование вызова
        self.logger.debug("Preparing match view data")
        
        # Инициализация данных по умолчанию
        score_data = {"sets": [0, 0], "games": [0, 0], "points": ["0", "0"]}

        # Получение актуального матча из репозитория
        current_match = self.repository.get_current_match()

        # Получаем имена игроков
        player1_name = (
            player_one_name_arg
            if player_one_name_arg is not None
            else (getattr(current_match, "player_one_name", "") if current_match else "")
        )
        player2_name = (
            player_two_name_arg
            if player_two_name_arg is not None
            else (getattr(current_match, "player_two_name", "") if current_match else "")
        )
        
        self.logger.debug(f"Display names: {player1_name} vs {player2_name}")

        error_message = None

        # Если есть данные о матче, парсим JSON со счетом
        if match_dto and match_dto.score:
            try:
                full_score = json.loads(match_dto.score)
                # Извлекаем только используемые поля
                score_data = {
                    "sets": full_score.get("sets", [0, 0]),
                    "games": full_score.get("games", [0, 0]),
                    "points": full_score.get("points", ["0", "0"]),
                }
                self.logger.debug(f"Parsed score data: {score_data}")
            except json.JSONDecodeError:
                error_message = "Error parsing match score data"
                self.logger.error("Failed to parse JSON score data")
        else:
            error_message = "Match data is unavailable."
            self.logger.warning("No match data available for display")

        # Оптимизированный контекст для шаблона
        context = {
            "score": score_data,
            "player_one_name": player1_name,
            "player_two_name": player2_name,
        }

        # Добавляем сообщение об ошибке, только если оно есть
        if error_message:
            context["error"] = error_message

        return context
