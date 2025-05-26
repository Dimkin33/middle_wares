"""CRUD-обработчик данных матчей: создание, получение, преобразование в DTO.

Не содержит игровой логики (подсчёта очков, определения победителя).
"""

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

    def list_matches_paginated(self, page: int = 1, per_page: int = 10) -> tuple[list[MatchDTO], int]:
        """Получить список матчей с пагинацией (DTO, total_pages)."""
        return self.repository.list_matches_paginated(page, per_page)