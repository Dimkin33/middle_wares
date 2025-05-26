"""DTO для моделей данных."""
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
