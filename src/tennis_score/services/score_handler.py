"""Обработчик игровой логики теннисного матча: только подсчёт очков и правила."""

import logging


class ScoreHandler:
    """Логика подсчёта очков, тай-брейков и определения победителя в матче."""
    def __init__(self):
        self.logger = logging.getLogger("service.score")

    def update_regular_score(self, match, player, player_score, opponent_score):
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
            self.check_set_win(match, player_score, opponent_score)
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
                self.check_set_win(match, player_score, opponent_score)

    def update_tiebreak_score(self, match, player, player_score, opponent_score):
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
            self.logger.info(f"Player {player} wins tiebreak: {p_score}-{o_score}")
            player_score["sets"] += 1
            player_score["games"] = 0
            opponent_score["games"] = 0
            player_score["tiebreak_points"] = 0
            opponent_score["tiebreak_points"] = 0
            player_score["points"] = 0
            opponent_score["points"] = 0
            match.is_tiebreak = False

    def check_set_win(self, match, player_score, opponent_score):
        """Проверяет, выиграл ли игрок сет, и запускает тай-брейк при 6:6.

        Args:
            match: объект матча
            player_score: счет игрока
            opponent_score: счет соперника
        """
        self.logger.debug(
            f"Checking set win: games {player_score['games']}-{opponent_score['games']}"
        )
        
        if player_score["games"] >= 6 and player_score["games"] >= opponent_score["games"] + 2:
            # Игрок выиграл сет с преимуществом в 2 или более гейма
            self.logger.info(
                f"Set won with score {player_score['games']}-{opponent_score['games']}"
            )
            player_score["sets"] += 1
            player_score["games"] = 0
            opponent_score["games"] = 0
            player_score["points"] = 0
            opponent_score["points"] = 0
        elif player_score["games"] == 6 and opponent_score["games"] == 6:
            # Ничья 6:6, начинаем тай-брейк
            self.logger.info("Tiebreak started at 6-6")
            match.is_tiebreak = True
            player_score["tiebreak_points"] = 0
            opponent_score["tiebreak_points"] = 0
            player_score["points"] = 0
            opponent_score["points"] = 0

    def reset_match_score(self, match):
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
