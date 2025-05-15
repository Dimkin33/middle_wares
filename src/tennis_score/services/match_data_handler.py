"""Обработчик данных матча для работы с матчами."""

import logging

from ..dto.match_dto import MatchDTO


class MatchDataHandler:
    """Класс для обработки данных матчей и преобразования между моделями и DTO."""

    def __init__(self, repository):
        """Инициализация обработчика данных матчей.
        
        Args:
            repository: репозиторий для доступа к данным матчей
        """
        self.repository = repository
        self.logger = logging.getLogger("service.match_data")

    def create_match(self, player_one_name: str, player_two_name: str) -> MatchDTO:
        """Создание нового матча.
        
        Args:
            player_one_name: имя первого игрока
            player_two_name: имя второго игрока
            
        Returns:
            MatchDTO: DTO с данными созданного матча
        """
        self.logger.debug(f"Creating new match: {player_one_name} vs {player_two_name}")
        
        # Создаем матч через репозиторий
        match = self.repository.create_match(player_one_name, player_two_name)
        
        # Получаем DTO матча
        match_dto = match.get_match_data()
        self.logger.info(f"New match created with UUID: {match_dto.uuid}")
        
        return match_dto

    def get_current_match_data(self) -> MatchDTO | None:
        """Получение данных текущего матча.
        
        Returns:
            MatchDTO: DTO с данными текущего матча или None, если матч не найден
        """
        # Получаем текущий матч из репозитория
        match = self.repository.get_current_match()
        
        if not match:
            self.logger.warning("No active match found")
            return None
            
        # Преобразуем в DTO
        self.logger.debug(f"Retrieved current match: {match.uuid}")
        return match.get_match_data()
        
    def check_match_winner(self, player: str, player_score: dict) -> bool:
        """Проверяет, выиграл ли игрок матч.
        
        Args:
            player: идентификатор игрока
            player_score: счет игрока
            
        Returns:
            bool: True, если игрок выиграл матч
        """
        if player_score["sets"] >= 2:
            self.logger.info(f"Match won by {player}")
            return True
        return False
