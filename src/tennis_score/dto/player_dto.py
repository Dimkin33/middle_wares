"""Модуль player_dto.

Содержит функции и классы для работы с теннисным скорингом.
"""

from dataclasses import dataclass


@dataclass
class PlayerDTO:
    """DTO для передачи данных игрока."""

    id: int
    name: str
