"""DTO для моделей данных."""
from dataclasses import dataclass


@dataclass
class MatchDTO:
    """DTO для передачи данных матча."""

    id: int | None  # Для БД, если есть
    uuid: str
    player1: str  # Изменено с int на str для имени игрока
    player2: str  # Изменено с int на str для имени игрока
    winner: str | None  # Изменено с int на str для имени игрока
    score: dict | str  # Может быть словарем для live score или строкой для final score
