"""Модель матча в теннисном приложении."""
import uuid

from .player import Player


class Match:
    """Модель теннисного матча, хранящая текущее состояние.

    Attributes:
        match_uid (str): Уникальный идентификатор матча (UUID).
        players (Dict[str, Player]): Словарь игроков {'player1': Player, 'player2': Player}.
        score_values (list[str]): Значения очков ('0', '15', '30', '40').
        scores (Dict[str, Dict]): Состояние счёта (сеты, геймы, очки, тай-брейк).
        is_tiebreak (bool): Флаг тай-брейка.
        winner (int | None): ID победителя (Player.id).
        id (int | None): ID матча в базе данных.
        _player1_id (int | None): ID первого игрока из базы (PlayerORM.id).
        _player2_id (int | None): ID второго игрока из базы (PlayerORM.id).
    """
    def __init__(self, player_one_name: str = "Игрок 1", player_two_name: str = "Игрок 2"):
        if not player_one_name or not player_two_name:
            raise ValueError("Имена игроков не могут быть пустыми")
        if player_one_name == player_two_name:
            raise ValueError("Игроки должны быть разными")

        self.match_uid: str = str(uuid.uuid4())
        self._player_one_obj: Player = Player(player_one_name)
        self._player_two_obj: Player = Player(player_two_name)
        self.players: dict[str, Player] = {"player1": self._player_one_obj, "player2": self._player_two_obj}
        self._player1_id: int | None = None
        self._player2_id: int | None = None
        self.score_values: list[str] = ["0", "15", "30", "40"]
        self.scores: dict[str, dict] = {
            "player1": {"sets": 0, "games": 0, "points": 0, "advantage": False, "tiebreak_points": 0},
            "player2": {"sets": 0, "games": 0, "points": 0, "advantage": False, "tiebreak_points": 0},
        }
        self.is_tiebreak: bool = False
        self.winner: int | None = None
        self.id: int | None = None
        self.set_scores_history: list[tuple[int, int]] = []  # История счета по геймам в завершенных сетах

    @property
    def player_one_name(self) -> str:
        """Имя первого игрока."""
        return self._player_one_obj.name

    @property
    def player_two_name(self) -> str:
        """Имя второго игрока."""
        return self._player_two_obj.name

    def set_player_ids(self, player1_id: int | None, player2_id: int | None) -> None:
        """Устанавливает ID игроков из базы."""
        self._player1_id = player1_id
        self._player2_id = player2_id
        self._player_one_obj.id = player1_id
        self._player_two_obj.id = player2_id

    def _format_points(self, player: str, opponent: str) -> str:
        """Форматирует очки игрока для отображения."""
        p = self.scores[player]
        o = self.scores[opponent]
        if p["advantage"]:
            return "AD"
        if o["advantage"]:
            return ""
        if p["points"] < len(self.score_values):
            return self.score_values[p["points"]]
        return str(p["points"])

    def set_winner(self, player_key: str) -> None:
        """Устанавливает победителя матча."""
        if player_key not in self.players:
            raise ValueError("Некорректный ключ игрока")
        self.winner = self._player1_id if player_key == "player1" else self._player2_id

    def add_completed_set_score(self, player1_set_games: int, player2_set_games: int) -> None:
        """Добавляет счет завершенного сета в историю."""
        self.set_scores_history.append((player1_set_games, player2_set_games))

    def get_final_score_str(self) -> str:
        """Возвращает строку итогового счета.

        Если есть завершенные сеты, форматирует историю счета по геймам в них.
        Например: "6-0, 6-2".
        В противном случае, возвращает текущий общий счет по сетам (например, "0-0").
        """
        if self.set_scores_history:
            return ", ".join([f"{s[0]}-{s[1]}" for s in self.set_scores_history])
        # Если история пуста, возвращаем текущий счет по выигранным сетам
        return f'{self.scores["player1"]["sets"]}-{self.scores["player2"]["sets"]}'

    def to_live_dto(self):
        """Вернуть DTO с live-структурой счёта (dict)."""
        from ..dto.match_dto import MatchDTO
        return MatchDTO(
            id=self.id or 0,
            uuid=self.match_uid,
            player1=self.player_one_name,
            player2=self.player_two_name,
            winner=None,
            score={
                "sets": [self.scores["player1"].get("sets", 0), self.scores["player2"].get("sets", 0)],
                "games": [self.scores["player1"].get("games", 0), self.scores["player2"].get("games", 0)],
                "points": [
                    self._format_points("player1", "player2"),
                    self._format_points("player2", "player1"),
                ],
            },
        )

    def to_final_dto(self):
        from ..dto.match_dto import MatchDTO
        if self.winner == self._player1_id:
            winner_name = self.player_one_name
        elif self.winner == self._player2_id:
            winner_name = self.player_two_name
        else:
            winner_name = None
        return MatchDTO(
            id=self.id or 0,
            uuid=self.match_uid,
            player1=self.player_one_name,
            player2=self.player_two_name,
            winner=winner_name,
            score=self.get_final_score_str(),
        )