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

    def create_match(self, player_one_name: str, player_two_name: str) -> MatchDTO:
        """Создать новый матч и вернуть DTO.

        Args:
            player_one_name: имя первого игрока.
            player_two_name: имя второго игрока.

        Returns:
            MatchDTO: DTO с данными созданного матча.
        """
        self.logger.debug(f"Creating new match: {player_one_name} vs {player_two_name}")
        match = self.repository.create_match(player_one_name, player_two_name)
        match_dto = match.get_match_data()
        self.logger.info(f"New match created with UUID: {match_dto.uuid}")
        return match_dto

    def get_current_match_data(self) -> MatchDTO | None:
        """Получить данные текущего матча (DTO) или None, если матч не найден."""
        match = self.repository.get_current_match()
        if not match:
            self.logger.warning("No active match found")
            return None
        self.logger.debug(f"Retrieved current match: {match.uuid}")
        return match.get_match_data()

    def get_match_by_uuid(self, match_uuid: str) -> MatchDTO | None:
        """Получить матч по UUID (DTO) или None, если не найден."""
        match = self.repository.get_match_by_uuid(match_uuid)
        if not match:
            self.logger.warning(f"Match not found: {match_uuid}")
            return None
        self.logger.debug(f"Retrieved match by UUID: {match_uuid}")
        return match.get_match_data()

    def list_matches(self) -> list[MatchDTO]:
        """Получить список всех матчей в виде DTO."""
        matches = self.repository.list_matches()
        return [m.get_match_data() for m in matches]
