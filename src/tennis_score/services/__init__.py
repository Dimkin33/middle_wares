"""Пакет для сервисов бизнес-логики теннисного приложения.

Содержит сервисы для работы с матчами, счетом и представлением данных.

Экспортируемые компоненты:
- MatchDataHandler: обработка и хранение данных матчей
- MatchService: основной сервис для управления матчами
- ScoreHandler: логика подсчёта очков и правил тенниса
- ViewDataHandler: подготовка данных для отображения в шаблонах
"""

from .match_data_handler import MatchDataHandler  # Работа с данными матчей (CRUD, поиск)
from .match_service import MatchService  # Главный сервис, координирует бизнес-логику
from .score_handler import ScoreHandler  # Подсчёт очков, правила, переходы состояний
from .view_data_handler import ViewDataHandler  # Формирование данных для UI/шаблонов

__all__ = [
    "MatchDataHandler",   # Класс для работы с данными матчей
    "MatchService",       # Главный сервис управления матчами
    "ScoreHandler",       # Подсчёт очков и логика правил
    "ViewDataHandler",    # Подготовка данных для отображения
]
