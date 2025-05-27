"""Обработчик игровой логики теннисного матча: только подсчёт очков и правила."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.tennis_score.model.match import Match


class ScoreHandler:
    """Логика подсчёта очков, тай-брейков и определения победителя в матче."""
    def __init__(self) -> None:
        self.logger: logging.Logger = logging.getLogger("service.score")

    def _check_and_set_match_winner(
        self,
        match: 'Match',
        player_key: str,  # "player1" or "player2"
        player_score: dict[str, int | bool],
    ) -> None:
        """Проверяет, выиграл ли игрок матч, и устанавливает победителя, если да."""
        # Предполагаем, что у матча есть атрибут SETS_TO_WIN, иначе по умолчанию 2
        sets_to_win = getattr(match, "SETS_TO_WIN", 2)
        if player_score.get("sets", 0) >= sets_to_win:
            match.set_winner(player_key)
            self.logger.info(
                f"Player {player_key} has won the match with {player_score.get('sets', 0)} sets."
            )

    def update_regular_score(
        self,
        match: 'Match',
        player: str,  # "player1" or "player2"
        player_score: dict[str, int | bool],
        opponent_score: dict[str, int | bool],
    ) -> None:
        """Обновляет счёт в обычной игре (не тай-брейк).

        Args:
            match: объект матча
            player: идентификатор игрока
            player_score: счет игрока
            opponent_score: счет соперника
        """
        score = player_score["points"]
        opponent_points = opponent_score["points"]
        
        self.logger.debug(
            f"Updating regular score: player {player} has {match.score_values[score]} points, "
            f"opponent has {match.score_values[opponent_points]} points"
        )

        if player_score["advantage"]:
            # Игрок с преимуществом набирает еще одно очко = выигрывает гейм
            self.logger.info(f"Player {player} with advantage scores a point and wins the game")
            player_score["advantage"] = False
            opponent_score["advantage"] = False
            player_score["games"] += 1
            player_score["points"] = 0
            opponent_score["points"] = 0
            # self.check_set_win(match, player_score, opponent_score) # Старый вызов
            self.check_set_win(match, player, player_score, opponent_score) # Новый вызов
        elif score < len(match.score_values) - 1:
            # Обычное увеличение очков (0->15->30->40)
            old_points = match.score_values[score]
            player_score["points"] += 1
            new_points = match.score_values[player_score["points"]]
            self.logger.debug(f"Player {player} scores: {old_points} -> {new_points}")
        elif score == len(match.score_values) - 1:
            # Игрок имеет 40 очков
            if opponent_points == len(match.score_values) - 1:
                # Соперник тоже имеет 40 очков
                if opponent_score["advantage"]:
                    # Соперник имел преимущество, теперь оно снимается (равенство)
                    self.logger.info(f"Player {player} scores: advantage removed, now DEUCE")
                    opponent_score["advantage"] = False
                else:
                    # Игрок получает преимущество
                    self.logger.info(f"Player {player} scores and gets ADVANTAGE")
                    player_score["advantage"] = True
            else:
                # Соперник имеет меньше 40 очков, игрок выигрывает гейм
                self.logger.info(f"Player {player} scores at 40 and wins the game")
                player_score["games"] += 1
                player_score["points"] = 0
                opponent_score["points"] = 0
                opponent_score["advantage"] = False
                # self.check_set_win(match, player_score, opponent_score) # Старый вызов
                self.check_set_win(match, player, player_score, opponent_score) # Новый вызов

    def update_tiebreak_score(
        self,
        match: 'Match',
        player: str, # "player1" or "player2"
        player_score: dict[str, int | bool],
        opponent_score: dict[str, int | bool],
    ) -> None:
        """Обновляет счёт в тай-брейке.

        Args:
            match: объект матча
            player: идентификатор игрока
            player_score: счет игрока
            opponent_score: счет соперника
        """
        # Добавляем подробное логирование 
        self.logger.debug(
            f"Updating tiebreak: player {player} has {player_score['tiebreak_points']} points, "
            f"opponent has {opponent_score['tiebreak_points']} points"
        )
        
        player_score["tiebreak_points"] += 1
        points = player_score["tiebreak_points"]
        self.logger.debug(f"Player {player} scores in tiebreak: now {points} points")
        
        # Проверка победы: 7 очков и преимущество в 2
        win_condition = (
            player_score["tiebreak_points"] >= 7 and 
            player_score["tiebreak_points"] >= opponent_score["tiebreak_points"] + 2
        )
        
        if win_condition:
            p_score = player_score["tiebreak_points"]
            o_score = opponent_score["tiebreak_points"]
            self.logger.info(
                f"Player {player} wins tiebreak and set. Score: {p_score}-{o_score}. "
                f"Total sets for {player}: {player_score.get('sets',0)}"
            )

            # Записываем счет сета в историю перед сбросом
            player1_games_in_set = 7 if player == "player1" else 6
            player2_games_in_set = 7 if player == "player2" else 6
            match.add_completed_set_score(player1_games_in_set, player2_games_in_set)

            player_score["sets"] += 1 # Увеличиваем счет сетов
            player_score["games"] = 0
            opponent_score["games"] = 0
            player_score["tiebreak_points"] = 0
            opponent_score["tiebreak_points"] = 0
            player_score["points"] = 0
            opponent_score["points"] = 0
            match.is_tiebreak = False
            self._check_and_set_match_winner(match, player, player_score) # Проверяем на победителя матча

    def check_set_win(
        self,
        match: 'Match',
        player_key: str, # Добавлен параметр player_key ("player1" or "player2")
        player_score: dict[str, int | bool],
        opponent_score: dict[str, int | bool],
    ) -> None:
        """Проверяет, выиграл ли игрок сет, и запускает тай-брейк при 6:6.

        Args:
            match: объект матча
            player_key: идентификатор игрока ("player1" или "player2")
            player_score: счет игрока
            opponent_score: счет соперника
        """
        self.logger.debug(
            f"Checking set win: games {player_score['games']}-{opponent_score['games']}"
        )
        
        pg = player_score["games"]
        og = opponent_score["games"]
        
        set_won = False
        if pg >= 6 and pg >= og + 2 or pg == 7 and og == 5:
            set_won = True
        # Случай 7-6 не обрабатывается здесь, так как он должен проходить через тай-брейк.
        # Однако, если логика тай-брейка не вызывается, а сет завершается 7-6 (например, если это правило), 
        # то это условие нужно будет добавить или изменить.
        # Текущая логика предполагает, что 7-6 возможно только после тай-брейка.

        if set_won:
            self.logger.info(
                f"Player {player_key} won set with score {pg}-{og}"
            )
            # Записываем счет сета в историю перед сбросом
            if player_key == "player1":
                match.add_completed_set_score(pg, og)
            else: # player_key == "player2"
                match.add_completed_set_score(og, pg)
            
            player_score["sets"] += 1
            player_score["games"] = 0
            opponent_score["games"] = 0
            player_score["points"] = 0
            opponent_score["points"] = 0
            self._check_and_set_match_winner(match, player_key, player_score) # Проверяем на победителя матча
        elif player_score["games"] == 6 and opponent_score["games"] == 6:
            # Ничья 6:6, начинаем тай-брейк
            self.logger.info("Tiebreak started at 6-6")
            match.is_tiebreak = True
            player_score["tiebreak_points"] = 0
            opponent_score["tiebreak_points"] = 0
            player_score["points"] = 0
            opponent_score["points"] = 0

    def reset_match_score(self, match: 'Match') -> None:
        """Сбрасывает счет матча.
        
        Args:
            match: объект матча, счет которого нужно сбросить
        """
        # Сбрасываем счет матча до начального состояния
        match.scores = {
            "player1": {
                "sets": 0,
                "games": 0,
                "points": 0,
                "advantage": False,
                "tiebreak_points": 0,
            },
            "player2": {
                "sets": 0,
                "games": 0,
                "points": 0,
                "advantage": False,
                "tiebreak_points": 0,
            },
        }
        match.is_tiebreak = False
        match.winner = None
        self.logger.info("Match score reset to initial state")
