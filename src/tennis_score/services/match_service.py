"""Фасад для работы с матчами: только координация обработчиков, без бизнес-логики."""

import logging

from ..core.presentation import ViewDataHandler
from ..dto.match_dto import MatchDTO
from ..repositories.orm_repository import OrmMatchRepository
from .match_data_handler import MatchDataHandler
from .score_handler import ScoreHandler


class MatchService:
    """Фасад для работы с матчами: координирует обработчики, не реализует бизнес-логику."""
    def __init__(self):
        self.logger = logging.getLogger("service")
        self.repository = OrmMatchRepository()  # Используем ORM-репозиторий
        self.score_handler = ScoreHandler()
        self.view_handler = ViewDataHandler()
        self.data_handler = MatchDataHandler(self.repository)
        self.logger.debug("MatchService initialized with ORM repository and handlers")

    def create_match(self, player_one_name: str, player_two_name: str) -> MatchDTO:
        return self.data_handler.create_match(player_one_name, player_two_name)

    def get_match_data_by_uuid(self, match_uuid: str) -> MatchDTO | None:
        """Получить данные матча по UUID."""
        return self.data_handler.get_match_data_by_uuid(match_uuid)

    def update_match_score(self, match_uuid: str, player: str) -> MatchDTO | None:
        """Обновить счет указанного матча для указанного игрока."""
        match = self.repository.get_active_match_by_uuid(match_uuid)
        if not match:
            self.logger.warning(f"No active match found with UUID {match_uuid} to update score")
            return None

        # Убедимся, что ID игроков установлены в объекте Match.
        # Используем getattr для безопасной проверки, существуют ли атрибуты.
        player_one_id_exists = getattr(match, 'player_one_id', None) is not None
        player_two_id_exists = getattr(match, 'player_two_id', None) is not None

        if not player_one_id_exists or not player_two_id_exists:
            self.logger.debug(
                f"Player IDs not set for match {match.match_uid}. Fetching/creating and setting them."
            )
            player1_id_db = self.repository.get_or_create_player_by_name(match.player_one_name)
            player2_id_db = self.repository.get_or_create_player_by_name(match.player_two_name)
            match.set_player_ids(player1_id_db, player2_id_db)
            # Объект match был изменен, current_match в репозитории - это ссылка на этот же объект.

        if player not in ["player1", "player2"]:
            self.logger.error(f"Invalid player identifier: {player}")
            return match.to_live_dto() # ID игроков теперь точно будут в DTO
        if match.winner: # Если победитель уже был определен ранее
            self.logger.warning("Attempted to update score for a completed match")
            return match.to_final_dto()

        player_score = match.scores[player]
        opponent = "player2" if player == "player1" else "player1"
        opponent_score = match.scores[opponent]
        try:
            if match.is_tiebreak:
                self.score_handler.update_tiebreak_score(match, player, player_score, opponent_score)
            else:
                self.score_handler.update_regular_score(match, player, player_score, opponent_score)
            
            # Логика определения победителя матча и сохранения перенесена в ScoreHandler.
            # Вызывается внутри update_regular_score/update_tiebreak_score -> check_set_win 
            # -> _check_and_set_match_winner.

            if match.winner: # Проверяем, определен ли победитель матча в ScoreHandler
                # Если победитель определен, значит матч завершен.
                # ID игроков уже установлены в объекте match ранее.
                self.repository.save_finished_match(match)
                self.logger.info(f"Match finished and saved: {match.match_uid}. Winner: {match.winner}")
                return match.to_final_dto()

            return match.to_live_dto()
        except Exception as e:
            self.logger.error(f"Error updating score: {e}", exc_info=True)
            # Возвращаем DTO с актуальными (возможно, только что установленными) ID
            return match.to_live_dto() if match else None

    def reset_match_score(self, match_uuid: str) -> None:
        """Сбросить счет указанного матча."""
        match = self.repository.get_active_match_by_uuid(match_uuid)
        if not match:
            self.logger.warning(f"No active match with UUID {match_uuid} to reset")
            return
        self.score_handler.reset_match_score(match)
        self.logger.info(f"Match {match_uuid} reset completed")

    def prepare_match_view_data(
        self,
        match_dto: MatchDTO | None,
    ) -> dict:
        return self.view_handler.prepare_match_view_data(
            match_dto
        )

    def get_completed_match_by_uuid(self, match_uuid: str) -> dict | None:
        """Получить завершенный матч из базы данных по UUID."""
        try:
            completed_match = self.repository.get_completed_match_by_uuid(match_uuid)
            if completed_match:
                self.logger.debug(f"Found completed match {match_uuid} in database")
                return completed_match
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving completed match {match_uuid}: {e}")
            return None

    def prepare_completed_match_view_data(self, completed_match: dict) -> dict:
        """Подготовить данные для отображения завершенного матча."""
        try:
            return {
                "match_uuid": completed_match.get("match_uid", ""),
                "player_one_name": completed_match.get("player_one_name", "N/A"),
                "player_two_name": completed_match.get("player_two_name", "N/A"),
                "winner": completed_match.get("winner", "N/A"),
                "final_score": completed_match.get("final_score", "Данные недоступны"),
                "completed_at": completed_match.get("completed_at", ""),
                "info": f"Матч завершен. Победитель: {completed_match.get('winner', 'N/A')}",
                "score": {
                    "sets": [0, 0],  # Данные сетов можно извлечь из final_score если нужно
                    "games": [0, 0],
                    "points": ["0", "0"]
                }
            }
        except Exception as e:
            self.logger.error(f"Error preparing completed match view data: {e}")
            return {
                "match_uuid": completed_match.get("match_uid", "") if completed_match else "",
                "player_one_name": "N/A",
                "player_two_name": "N/A",
                "winner": "N/A",
                "error": "Ошибка при подготовке данных матча",
                "score": {"sets": [0, 0], "games": [0, 0], "points": ["0", "0"]}
            }
