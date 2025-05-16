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
        """Создать новый матч и вернуть DTO."""
        self.logger.debug(f"Creating new match: {player_one_name} vs {player_two_name}")
        match = self.repository.create_match(player_one_name, player_two_name)
        # Для ORM-репозитория match — это ORM-объект, преобразуем в DTO через orm_to_dto
        from ..repositories.orm_repository import orm_to_dto
        match_dto = orm_to_dto(match)
        self.logger.info(f"New match created with UUID: {match_dto.uuid}")
        return match_dto

    def get_current_match_data(self) -> MatchDTO | None:
        """Для ORM-репозитория всегда None (нет текущего матча)."""
        return None

    def get_match_by_uuid(self, match_uuid: str) -> MatchDTO | None:
        # TODO: реализовать поиск по UUID через ORM
        return None

    def list_matches(self) -> list[MatchDTO]:
        """Получить список всех матчей в виде DTO."""
        return self.repository.list_matches()
