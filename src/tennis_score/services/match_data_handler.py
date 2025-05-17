"""CRUD-обработчик данных матчей: создание, получение, преобразование в DTO.

Не содержит игровой логики (подсчёта очков, определения победителя).
"""

import json
import logging

from ..dto.match_dto import MatchDTO


class MatchDataHandler:
    """Работа с данными матчей: создание, получение, преобразование в DTO.

    Не содержит игровой логики (подсчёта очков, определения победителя).
    """

    def __init__(self, repository):
        """Инициализация обработчика данных матчей.

        Args:
            repository: репозиторий для доступа к данным матчей.
        """
        self.repository = repository
        self.logger = logging.getLogger("service.match_data")
        self._current_match_dto = None  # Для хранения текущего матча в памяти

    def create_match(self, player_one_name: str, player_two_name: str) -> MatchDTO:
        """Создать новый матч и вернуть DTO."""
        self.logger.debug(f"Creating new match: {player_one_name} vs {player_two_name}")
        match_dto = self.repository.create_match(player_one_name, player_two_name)
        self._current_match_dto = match_dto  # Сохраняем текущий матч в памяти
        self.logger.info(f"New match created with UUID: {match_dto.uuid}")
        return match_dto

    def get_current_match_data(self) -> MatchDTO | None:
        """Вернуть текущий матч из памяти, если есть."""
        return self._current_match_dto

    def reset_current_match(self):
        self._current_match_dto = None

    def get_match_by_uuid(self, match_uuid: str) -> MatchDTO | None:
        # TODO: реализовать поиск по UUID через ORM
        return None

    def _format_score(self, score_json: str) -> str:
        """Преобразует JSON-строку счёта в красивый вид (например, 2:0)."""
        try:
            score = json.loads(score_json)
            sets = score.get("sets")
            if sets and isinstance(sets, list) and len(sets) == 2:
                return f"{sets[0]}:{sets[1]}"
        except Exception:
            pass
        return "-"

    def list_matches(self) -> list[MatchDTO]:
        """Получить список всех матчей в виде DTO с красивым счётом."""
        matches = self.repository.list_matches()
        for m in matches:
            if hasattr(m, 'score'):
                m.score_str = self._format_score(m.score)
        return matches
