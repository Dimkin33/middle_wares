"""CRUD-обработчик данных матчей: создание, получение, преобразование в DTO.

Не содержит игровой логики (подсчёта очков, определения победителя).
"""

import logging

from ..dto.match_dto import MatchDTO
from ..model.match import Match  # Added import


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
        # self._current_match_dto = None  # Удалено: больше не храним текущий матч здесь

    def create_match(self, player_one_name: str, player_two_name: str) -> MatchDTO:
        """Создать новый матч и вернуть DTO."""
        self.logger.debug(f"Creating new match: {player_one_name} vs {player_two_name}")
        # match_dto = self.repository.create_match(player_one_name, player_two_name)
        # self._current_match_dto = match_dto  # Сохраняем текущий матч в памяти
        # self.logger.info(f"New match created with UUID: {match_dto.uuid}")
        # return match_dto
        match_instance: Match = self.repository.create_match(player_one_name, player_two_name)
        # match_dto = MatchDTO.from_match(match_instance)  # Преобразование Match в MatchDTO <-- ОШИБКА ЗДЕСЬ
        match_dto = match_instance.to_live_dto() # Получаем DTO из объекта Match
        self.logger.info(f"New match created with UUID: {match_dto.uuid}")
        return match_dto

    # def get_current_match_data(self) -> MatchDTO | None:
    #     """Вернуть текущий матч из памяти, если есть."""
    #     return self._current_match_dto

    def get_match_data_by_uuid(self, match_uuid: str) -> MatchDTO | None:
        """Вернуть данные матча по UUID из активных матчей."""
        self.logger.debug(f"Attempting to get match data for UUID: {match_uuid}")
        match_instance = self.repository.get_active_match_by_uuid(match_uuid)
        if match_instance:
            self.logger.debug(f"Active match found for UUID: {match_uuid}")
            return MatchDTO.from_match(match_instance)
        self.logger.debug(f"No active match found for UUID: {match_uuid}. Attempting to fetch from DB.")
        # Попытка загрузить из БД, если не найден в активных (например, завершенный матч)
        # Это предполагает, что в репозитории есть метод для получения матча из БД по UUID
        # и преобразования его в объект Match, а затем в MatchDTO.
        # Если такого метода нет или это не требуется для активных матчей, эту часть можно опустить
        # или изменить логику.
        # Для примера, предположим, что репозиторий может вернуть MatchDTO напрямую из БД
        # или мы можем загрузить объект Match и преобразовать его.
        match_from_db = self.repository.get_match_by_uuid_from_db(match_uuid)  # Предполагаемый метод
        if match_from_db:
            self.logger.debug(f"Match found in DB for UUID: {match_uuid}")
            # Если get_match_by_uuid_from_db возвращает объект Match, а не MatchDTO:
            # return MatchDTO.from_match(match_from_db)
            # Если он уже возвращает MatchDTO:
            return match_from_db
        self.logger.warning(f"Match with UUID {match_uuid} not found in active matches or DB.")
        return None

    def list_matches_paginated(
        self, page: int = 1, per_page: int = 10, filter_query: str | None = None
    ) -> tuple[list[MatchDTO], int]:
        """Получить список матчей с пагинацией (DTO, total_pages), опционально с фильтром."""
        self.logger.debug(f"Listing matches for page {page}, per_page {per_page}, filter: '{filter_query}'")
        return self.repository.list_matches_paginated(page, per_page, filter_query)