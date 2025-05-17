"""ORM-репозиторий для работы с базой данных теннисных матчей."""
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..dto.match_dto import MatchDTO
from ..dto.player_dto import PlayerDTO

# --- ИМПОРТ ORM-МОДЕЛЕЙ ---
from ..model.orm_models import Base, MatchORM, PlayerORM

# Настройка логирования
logger = logging.getLogger("orm")
logging.basicConfig(level=logging.INFO)

# Настройка SQLAlchemy
engine = create_engine("sqlite:///tennis_score.db", echo=False)
Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    """Контекстный менеджер для безопасной работы с сессией."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("Ошибка при работе с БД: %s", e)
        raise
    finally:
        session.close()


def init_db(force: bool = False):
    """Инициализация базы данных (создание таблиц).
    
    Args:
        force (bool): если True — удаляет и пересоздаёт таблицы
    """
    if force:
        Base.metadata.drop_all(engine)
        logger.warning("База данных сброшена!")
    Base.metadata.create_all(engine)
    logger.info("База данных инициализирована.")


# CRUD-функции

def add_player(name: str) -> PlayerORM:
    """Добавление игрока в БД."""
    with get_session() as session:
        player = PlayerORM(name=name)
        session.add(player)
        logger.info(f"Добавлен игрок: {player}")
        return player


def add_match(uuid: str, player1_id: int, player2_id: int, winner_id: int, score: str) -> MatchORM:
    """Добавление матча в БД."""
    with get_session() as session:
        match = MatchORM(
            uuid=uuid,
            player1_id=player1_id,
            player2_id=player2_id,
            winner_id=winner_id,
            score_str=score,
        )
        session.add(match)
        logger.info(f"Добавлен матч: {match}")
        return match


def list_matches() -> list[MatchORM]:
    """Получение списка матчей."""
    with get_session() as session:
        matches = session.query(MatchORM).order_by(MatchORM.created_at.desc()).all()
        logger.info(f"Найдено матчей: {len(matches)}")
        return matches


def list_players() -> list[PlayerORM]:
    """Получение списка игроков."""
    with get_session() as session:
        players = session.query(PlayerORM).order_by(PlayerORM.name).all()
        logger.info(f"Найдено игроков: {len(players)}")
        return players


def get_player_by_id(player_id: int) -> PlayerORM | None:
    """Получить игрока по id."""
    with get_session() as session:
        return session.query(PlayerORM).filter_by(id=player_id).first()


def get_player_by_name(name: str) -> PlayerORM | None:
    """Получить игрока по имени."""
    with get_session() as session:
        return session.query(PlayerORM).filter_by(name=name).first()


def get_or_create_player_by_name(name: str) -> int:
    """Получить id игрока по имени или создать, если не найден."""
    with get_session() as session:
        player = session.query(PlayerORM).filter_by(name=name).first()
        if player:
            return player.id
        player = PlayerORM(name=name)
        session.add(player)
        session.flush()  # чтобы получить id
        logger.info(f"Создан новый игрок: {player}")
        return player.id


def player_orm_to_dto(player: PlayerORM) -> PlayerDTO:
    """Преобразование ORM-игрока в DTO."""
    return PlayerDTO(id=player.id, name=player.name)


def orm_to_dto(match: MatchORM, session=None) -> MatchDTO:
    """Преобразование ORM-объекта матча в DTO с именами игроков."""
    close_session = False
    if session is None:
        close_session = True
        session = Session()
    try:
        player1_name = None
        player2_name = None
        winner_name = None
        if match.player1_id:
            player1 = session.query(PlayerORM).get(match.player1_id)
            player1_name = player1.name if player1 else None
        if match.player2_id:
            player2 = session.query(PlayerORM).get(match.player2_id)
            player2_name = player2.name if player2 else None
        if match.winner_id:
            winner = session.query(PlayerORM).get(match.winner_id)
            winner_name = winner.name if winner else None
        return MatchDTO(
            id=match.id,
            uuid=match.uuid,
            player1=player1_name,
            player2=player2_name,
            winner=winner_name,
            score=match.score_str,
        )
    finally:
        if close_session:
            session.close()

def list_matches_dto() -> list[MatchDTO]:
    """Получение списка матчей в виде DTO."""
    with get_session() as session:
        matches = session.query(MatchORM).all()
        return [orm_to_dto(m, session) for m in matches]


class OrmMatchRepository:
    """Репозиторий для работы с матчами через ORM (SQLite)."""
    def __init__(self):
        self.finished_matches = []
        self._current_match = None  # Для хранения текущего матча в памяти
        self._current_match_dto = None  # Для хранения текущего матча в памяти

    def create_match(self, player_one_name: str, player_two_name: str):
        from ..model.match import Match
        match = Match(player_one_name, player_two_name)
        self._current_match = match  # Сохраняем бизнес-объект, а не только DTO
        return match.get_match_data()

    def save_finished_match(self, match):
        # Получаем id игроков через get_or_create_player_by_name (теперь возвращает id)
        player1_id = get_or_create_player_by_name(match.player_one_name)
        player2_id = get_or_create_player_by_name(match.player_two_name)
        winner = None
        if match.winner == match.players["player1"].id:
            winner = player1_id
        elif match.winner == match.players["player2"].id:
            winner = player2_id
        # Сохраняем матч в БД
        add_match(
            uuid=match.match_uid,
            player1_id=player1_id,
            player2_id=player2_id,
            winner_id=winner,
            score=match.get_score_json(),
        )
        # Получаем матч из БД в новой сессии и преобразуем в DTO
        with get_session() as session:
            orm_match = session.query(MatchORM).filter_by(uuid=match.match_uid).first()
            return orm_to_dto(orm_match, session)

    def list_matches(self):
        # Возвращаем список DTO
        return list_matches_dto()

    def get_current_match(self):
        return getattr(self, '_current_match', None)

    def reset_current_match(self):
        self._current_match = None
        self._current_match_dto = None

    @property
    def current_match(self):
        return self._current_match

    @current_match.setter
    def current_match(self, value):
        self._current_match = value

    def get_match_by_uuid(self, match_uuid: str):
        # TODO: реализовать поиск по UUID через ORM и возвращать DTO
        pass
