"""Модуль содержит модель теннисного матча и связанные с ней классы и методы."""

# match.py

import json
import uuid

from ..dto.match_dto import MatchDTO
from .player import Player


class Match:
    """Модель теннисного матча, хранящая текущее состояние.
    Содержит только данные и методы доступа к ним.
    Бизнес-логика обновления счета перенесена в MatchService.
    """  # noqa: D205

    def __init__(self, player_one_name="Игрок 1", player_two_name="Игрок 2"):
        self.match_uid = str(uuid.uuid4())

        # Сохраняем имена напрямую для легкого доступа из контроллеров
        self.player_one_name = player_one_name
        self.player_two_name = player_two_name

        # Создаем объекты Player
        # Их атрибут .id будет строкой UUID
        self._player_one_obj = Player(player_one_name)
        self._player_two_obj = Player(player_two_name)

        # Для внутренней логики (подсчет очков и т.д.), используя ключи 'player1', 'player2'
        # self.players сопоставляет 'player1'/'player2' с объектами Player
        self.players = {"player1": self._player_one_obj, "player2": self._player_two_obj}

        # Для MatchDTO, который ожидает целочисленные ID для игроков
        # Здесь мы присваиваем статические целые числа.
        # Если бы игроки были из БД, это были бы их ID из БД.
        self._dto_player1_id = 1
        self._dto_player2_id = 2

        self.score_values = ["0", "15", "30", "40"]
        self.scores = {
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
        self.is_tiebreak = False
        # self.winner будет хранить строку UUID объекта Player-победителя
        self.winner = None
        self.id = None  # Для БД, если сам Match хранится

    def get_score_json(self):
        """Формирует JSON для сохранения счета."""

        # points: отображаемые значения (0, 15, 30, 40, AD)
        def display_point(val, adv, other_val, other_adv):
            # Если у одного игрока есть преимущество/AD, у другого пусто
            if adv:
                return "AD"
            if other_adv:
                return ""
            if val < len(self.score_values):
                return self.score_values[val]
            return str(val)

        p1 = self.scores["player1"]
        p2 = self.scores["player2"]
        score_obj = {
            "sets": [p1["sets"], p2["sets"]],
            "games": [p1["games"], p2["games"]],
            "points": [
                display_point(p1["points"], p1["advantage"], p2["points"], p2["advantage"]),
                display_point(p2["points"], p2["advantage"], p1["points"], p1["advantage"]),
            ],
            "advantage": [p1["advantage"], p2["advantage"]],
            "tiebreak_points": [p1["tiebreak_points"], p2["tiebreak_points"]],
            "is_tiebreak": self.is_tiebreak,
            "winner": self.winner,
            "score_values": self.score_values,
        }
        return json.dumps(score_obj, ensure_ascii=False)

    def get_match_data(self) -> MatchDTO:
        """Возвращает данные текущего матча в виде MatchDTO."""
        winner_dto_id = None
        if self.winner:  # self.winner это строка UUID объекта Player-победителя
            if self.winner == self._player_one_obj.id:
                winner_dto_id = self._dto_player1_id
            elif self.winner == self._player_two_obj.id:
                winner_dto_id = self._dto_player2_id

        return MatchDTO(
            id=self.id,  # Это Match.id (int | None)
            uuid=self.match_uid,  # str
            player1=self._dto_player1_id,  # int
            player2=self._dto_player2_id,  # int
            winner=winner_dto_id,  # int | None
            score=self.get_score_json(),  # str
        )
