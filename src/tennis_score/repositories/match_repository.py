"""Repository for managing tennis match objects."""

import logging

from ..model.match import Match


class MatchRepository:
    """Репозиторий для управления объектами матча.
    В будущем может быть расширен для работы с базой данных.
    """  # noqa: D205

    def __init__(self):
        self.logger = logging.getLogger("repository")
        self.current_match = None
        self.logger.debug("MatchRepository initialized")

    def create_match(self, player_one_name: str, player_two_name: str) -> Match:
        """Создает новый матч."""
        self.logger.debug(f"Creating match for players: {player_one_name}, {player_two_name}")
        self.current_match = Match(player_one_name, player_two_name)
        self.logger.debug(f"Match created with ID: {self.current_match.match_uid}")
        return self.current_match

    def get_current_match(self) -> Match | None:
        """Возвращает текущий активный матч."""
        has_match = self.current_match is not None
        self.logger.debug(f"Getting current match: {'found' if has_match else 'not found'}")
        return self.current_match

    def update_match_score(self, player: str) -> Match | None:
        """Возвращает объект матча для обновления счета.
        Фактическое обновление должно происходить в сервисном слое.
        """  # noqa: D205
        if not self.current_match:
            self.logger.warning("Attempted to update score but no active match found")
            return None

        self.logger.debug(f"Retrieving match for score update for player: {player}")
        return self.current_match

    def reset_current_match(self) -> None:
        """Проверяет наличие текущего матча для сброса.
        Фактический сброс должен происходить в сервисном слое.
        """  # noqa: D202, D205
        
        if not self.current_match:
            self.logger.warning("Attempted to reset match but no active match found")
            return

        self.logger.debug("Current match is available for reset")
