"""Модель игрока в теннисном приложении."""


class Player:
    """Модель игрока в теннисном приложении.

    Attributes:
        id (int | None): Уникальный идентификатор игрока, задаётся базой данных.
        name (str): Имя игрока (уникальное).
    """
    def __init__(self, name: str, id: int | None = None):
        if not name:
            raise ValueError("Имя игрока не может быть пустым")
        self.id: int | None = id
        self.name: str = name
