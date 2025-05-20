"""ViewDataHandler: подготовка данных для шаблонов (presentation/infrastructure layer)."""

import logging


class ViewDataHandler:
    """Готовит данные о матче для шаблонов. Не обращается к репозиторию напрямую."""
    def __init__(self):
        self.logger = logging.getLogger("presentation.view")

    def prepare_match_view_data(self, match_dto, player_one_name_arg=None, player_two_name_arg=None):
        """Подготовка данных для отображения матча.

        Args:
            match_dto: DTO матча или None
            player_one_name_arg: имя первого игрока (если передано)
            player_two_name_arg: имя второго игрока (если передано)

        Returns:
            dict: контекст для отображения матча в шаблонизаторе
        """
        self.logger.debug("Preparing match view data")
        score_data = {"sets": [0, 0], "games": [0, 0], "points": ["0", "0"]}
        player1_name = player_one_name_arg if player_one_name_arg else (
            getattr(match_dto, 'player1', '') if match_dto else ''
        )
        player2_name = player_two_name_arg if player_two_name_arg else (
            getattr(match_dto, 'player2', '') if match_dto else ''
        )
        self.logger.debug(f"Display names: {player1_name} vs {player2_name}")
        error_message = None
        if match_dto and match_dto.score:
            if isinstance(match_dto.score, dict):
                score_data = {
                    "sets": match_dto.score.get("sets", [0, 0]),
                    "games": match_dto.score.get("games", [0, 0]),
                    "points": match_dto.score.get("points", ["0", "0"]),
                }
                self.logger.debug(f"Parsed score data: {score_data}")
            else:
                # score — это красивая строка (для истории)
                score_data = match_dto.score
        else:
            error_message = "Match data is unavailable."
            self.logger.warning("No match data available for display")
        context = {
            "score": score_data,
            "player_one_name": player1_name,
            "player_two_name": player2_name,
        }
        if error_message:
            context["error"] = error_message
        return context
