import json  # noqa: D100
from dataclasses import dataclass


@dataclass
class MatchDTO:
    """DTO для передачи данных матча."""

    id: int | None  # Для БД, если есть
    uuid: str
    player1: int
    player2: int
    winner: int | None
    score: str  # JSON-строка для БД

    def to_json(self):
        return json.dumps(
            {
                "id": self.id,
                "uuid": self.uuid,
                "player1": self.player1,
                "player2": self.player2,
                "winner": self.winner,
                "score": self.score,
            },
            ensure_ascii=False,
        )
