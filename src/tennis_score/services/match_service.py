"""Фасад для работы с матчами: только координация обработчиков, без бизнес-логики."""

import logging

from ..dto.match_dto import MatchDTO
from ..core.presentation import ViewDataHandler
from ..repositories.match_repository import MatchRepository
from .match_data_handler import MatchDataHandler
from .score_handler import ScoreHandler


class MatchService:
    """Фасад для работы с матчами: координирует обработчики, не реализует бизнес-логику."""
    def __init__(self):
        self.logger = logging.getLogger("service")
        self.repository = MatchRepository()
        self.score_handler = ScoreHandler()
        self.view_handler = ViewDataHandler()
        self.data_handler = MatchDataHandler(self.repository)
        self.logger.debug("MatchService initialized with repository and handlers")

    def create_match(self, player_one_name: str, player_two_name: str) -> MatchDTO:
        return self.data_handler.create_match(player_one_name, player_two_name)

    def get_current_match_data(self) -> MatchDTO | None:
        return self.data_handler.get_current_match_data()

    def update_current_match_score(self, player: str) -> MatchDTO | None:
        match = self.repository.get_current_match()
        if not match:
            self.logger.warning("No active match found to update score")
            return None
        if player not in ["player1", "player2"]:
            self.logger.error(f"Invalid player identifier: {player}")
            return match.get_match_data()
        if match.winner:
            self.logger.warning("Attempted to update score for a completed match")
            return match.get_match_data()
        player_score = match.scores[player]
        opponent = "player2" if player == "player1" else "player1"
        opponent_score = match.scores[opponent]
        try:
            if match.is_tiebreak:
                self.score_handler.update_tiebreak_score(match, player, player_score, opponent_score)
            else:
                self.score_handler.update_regular_score(match, player, player_score, opponent_score)
            # Проверка победителя теперь должна быть в ScoreHandler, но для совместимости:
            if player_score.get("sets", 0) >= 2:
                match.winner = match.players[player].id
            self.repository.current_match = match
            return match.get_match_data()
        except Exception as e:
            self.logger.error(f"Error updating score: {e}")
            return match.get_match_data()

    def reset_current_match(self) -> None:
        match = self.repository.get_current_match()
        if not match:
            self.logger.warning("No active match to reset")
            return
        self.score_handler.reset_match_score(match)
        self.repository.current_match = match
        self.logger.info("Match reset completed")

    def prepare_match_view_data(
        self,
        match_dto: MatchDTO | None,
        player_one_name_arg: str | None = None,
        player_two_name_arg: str | None = None,
    ) -> dict:
        return self.view_handler.prepare_match_view_data(
            match_dto, player_one_name_arg, player_two_name_arg
        )
