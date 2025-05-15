"""Сервис для работы с теннисными матчами."""
import logging

from ..dto.match_dto import MatchDTO
from ..repositories.match_repository import MatchRepository
from .match_data_handler import MatchDataHandler
from .score_handler import ScoreHandler
from .view_data_handler import ViewDataHandler


class MatchService:
    """Сервис для работы с теннисными матчами.
    
    Отвечает за бизнес-логику и преобразование данных между моделями и DTO.
    """

    def __init__(self):
        """Инициализация сервиса матчей с необходимыми зависимостями."""
        self.logger = logging.getLogger("service")
        self.repository = MatchRepository()
        self.score_handler = ScoreHandler()
        self.view_handler = ViewDataHandler(self.repository)
        self.data_handler = MatchDataHandler(self.repository)
        self.logger.debug("MatchService initialized with repository and handlers")

    def create_match(self, player_one_name: str, player_two_name: str) -> MatchDTO:
        """Создание нового матча."""
        # Делегируем создание матча обработчику данных
        return self.data_handler.create_match(player_one_name, player_two_name)

    def get_current_match_data(self) -> MatchDTO | None:
        """Получение данных текущего матча."""
        # Делегируем получение данных текущего матча обработчику данных
        return self.data_handler.get_current_match_data()

    def update_current_match_score(self, player: str) -> MatchDTO | None:
        """Обновление счета в текущем матче.

        Args:
            player: идентификатор игрока ("player1" или "player2")

        Returns:
            MatchDTO: обновленные данные матча или None, если матч не найден
        """
        match = self.repository.get_current_match()
        if not match:
            self.logger.warning("No active match found to update score")
            return None

        # Проверка валидности входящих данных
        if player not in ["player1", "player2"]:
            self.logger.error(f"Invalid player identifier: {player}")
            return match.get_match_data()

        # Проверка, завершен ли матч
        if match.winner:
            self.logger.warning("Attempted to update score for a completed match")
            return match.get_match_data()

        # Получаем текущие счета для игроков
        player_score = match.scores[player]
        opponent = "player2" if player == "player1" else "player1"
        opponent_score = match.scores[opponent]

        try:
            # Применяем логику обновления счета в зависимости от режима игры
            if match.is_tiebreak:
                self.score_handler.update_tiebreak_score(match, player, player_score, opponent_score)
            else:
                self.score_handler.update_regular_score(match, player, player_score, opponent_score)

            # Проверяем, выиграл ли игрок матч, используя обработчик данных
            if self.data_handler.check_match_winner(player, player_score):
                match.winner = match.players[player].id

            # Сохраняем обновленный матч через репозиторий
            self.repository.current_match = match

            return match.get_match_data()
        except Exception as e:
            self.logger.error(f"Error updating score: {e}")
            return match.get_match_data()

    def reset_current_match(self) -> None:
        """Сброс текущего матча."""
        match = self.repository.get_current_match()
        if not match:
            self.logger.warning("No active match to reset")
            return

        # Используем обработчик счета для сброса
        self.score_handler.reset_match_score(match)
        
        # Сохраняем обновленный матч через репозиторий
        self.repository.current_match = match
        self.logger.info("Match reset completed")

# Эти методы были перемещены в ScoreHandler

    def prepare_match_view_data(
        self,
        match_dto: MatchDTO | None,
        player_one_name_arg: str | None = None,
        player_two_name_arg: str | None = None,
    ) -> dict:
        """Подготовка данных для отображения матча.
        
        Args:
            match_dto: DTO матча или None
            player_one_name_arg: имя первого игрока (если передано)
            player_two_name_arg: имя второго игрока (если передано)
            
        Returns:
            dict: контекст для отображения матча в шаблонизаторе
        """
        # Используем обработчик представления для подготовки данных
        return self.view_handler.prepare_match_view_data(
            match_dto, player_one_name_arg, player_two_name_arg
        )
