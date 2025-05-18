import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..dto.match_dto import MatchDTO
from ..dto.player_dto import PlayerDTO
from ..model.match import Match
from ..model.orm_models import Base, MatchORM, PlayerORM

# Настройка логирования
logger = logging.getLogger("orm")
logging.basicConfig(level=logging.INFO)

class OrmMatchRepository:
    """Репозиторий для работы с матчами и игроками через ORM (SQLite)."""
    def __init__(self, db_url: str = "sqlite:///tennis_score.db"):
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.finished_matches = []
        self._current_match = None

    @contextmanager
    def _get_session(self):
        """Контекстный менеджер для безопасной работы с сессией."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Ошибка при работе с БД: %s", e)
            raise
        finally:
            session.close()

    def init_db(self, force: bool = False):
        """Инициализация базы данных (создание таблиц)."""
        if force:
            Base.metadata.drop_all(self.engine)
            logger.warning("База данных сброшена!")
        Base.metadata.create_all(self.engine)
        logger.info("База данных инициализирована.")

    def add_player(self, name: str) -> PlayerORM:
        """Добавление игрока в БД."""
        if not name:
            raise ValueError("Имя игрока не может быть пустым")
        with self._get_session() as session:
            player = PlayerORM(name=name)
            session.add(player)
            logger.info(f"Добавлен игрок: {player}")
            return player

    def add_match(self, uuid: str, player1_id: int, player2_id: int, winner_id: int | None, score: str) -> int:
        """Добавление матча в БД. Возвращает id созданного матча."""
        if not uuid or not isinstance(uuid, str):
            raise ValueError("UUID матча должен быть непустой строкой")
        if player1_id == player2_id:
            raise ValueError("Игроки должны быть разными")
        if not score:
            raise ValueError("Счёт матча не может быть пустым")

        with self._get_session() as session:
            for pid in [player1_id, player2_id, winner_id]:
                if pid and not session.query(PlayerORM).get(pid):
                    raise ValueError(f"Игрок с ID {pid} не найден")
            match = MatchORM(
                uuid=uuid,
                player1_id=player1_id,
                player2_id=player2_id,
                winner_id=winner_id,
                score_str=score,
            )
            session.add(match)
            session.flush()  # Получить id
            logger.info(f"Добавлен матч: {match}")
            return match.id

    def list_matches(self) -> list[MatchDTO]:
        """Получение списка матчей в виде DTO (для шаблонов и API)."""
        with self._get_session() as session:
            matches = session.query(MatchORM).all()
            return [self.orm_to_dto(m) for m in matches]

    # Для обратной совместимости
    list_matches_dto = list_matches

    def list_players(self) -> list[PlayerORM]:
        """Получение списка игроков."""
        with self._get_session() as session:
            players = session.query(PlayerORM).order_by(PlayerORM.name).all()
            logger.info(f"Найдено игроков: {len(players)}")
            return players

    def get_player_by_id(self, player_id: int) -> PlayerORM | None:
        """Получить игрока по ID."""
        with self._get_session() as session:
            return session.query(PlayerORM).filter_by(id=player_id).first()

    def get_player_by_name(self, name: str) -> PlayerORM | None:
        """Получить игрока по имени."""
        with self._get_session() as session:
            return session.query(PlayerORM).filter_by(name=name).first()

    def get_or_create_player_by_name(self, name: str) -> int:
        """Получить ID игрока по имени или создать, если не найден."""
        if not name:
            raise ValueError("Имя игрока не может быть пустым")
        with self._get_session() as session:
            player = session.query(PlayerORM).filter_by(name=name).first()
            if player:
                return player.id
            player = PlayerORM(name=name)
            session.add(player)
            session.flush()
            logger.info(f"Создан новый игрок: {player}")
            return player.id

    def player_orm_to_dto(self, player: PlayerORM) -> PlayerDTO:
        """Преобразование ORM-игрока в DTO."""
        return PlayerDTO(id=player.id, name=player.name)

    def orm_to_dto(self, match: MatchORM) -> MatchDTO:
        """Преобразование ORM-объекта матча в DTO с именами игроков."""
        with self._get_session() as session:
            def get_player_name(player_id: int | None) -> str | None:
                if not player_id:
                    return None
                player = session.query(PlayerORM).get(player_id)
                return player.name if player else None
            return MatchDTO(
                id=match.id,
                uuid=match.uuid,
                player1=get_player_name(match.player1_id),
                player2=get_player_name(match.player2_id),
                winner=get_player_name(match.winner_id),
                score=match.score_str,
            )

    def create_match(self, player_one_name: str, player_two_name: str) -> MatchDTO:
        """Создать новый матч и сохранить его как текущий."""
        if not player_one_name or not player_two_name:
            raise ValueError("Имена игроков не могут быть пустыми")
        if player_one_name == player_two_name:
            raise ValueError("Игроки должны быть разными")

        match = Match(player_one_name, player_two_name)
        self._current_match = match

        player1_id = self.get_or_create_player_by_name(player_one_name)
        player2_id = self.get_or_create_player_by_name(player_two_name)

        return MatchDTO(
            id=0,
            uuid=match.match_uid,
            player1=player1_id,
            player2=player2_id,
            winner=None,
            score=match.get_score_json(),
        )

    def save_finished_match(self, match: Match) -> MatchDTO:
        """Сохранить завершённый матч в БД и вернуть его DTO."""
        if not match.player_one_name or not match.player_two_name:
            raise ValueError("Имена игроков не могут быть пустыми")

        player1_id = self.get_or_create_player_by_name(match.player_one_name)
        player2_id = self.get_or_create_player_by_name(match.player_two_name)
        winner_id = None
        if match.winner:
            winner_id = player1_id if match.winner == match.players["player1"].id else player2_id

        match_id = self.add_match(
            uuid=match.match_uid,
            player1_id=player1_id,
            player2_id=player2_id,
            winner_id=winner_id,
            score=match.get_score_json(),
        )
        with self._get_session() as session:
            orm_match = session.query(MatchORM).get(match_id)
            return self.orm_to_dto(orm_match)

    def get_match_by_uuid(self, match_uuid: str) -> MatchDTO | None:
        """Получить матч по UUID в формате DTO."""
        if not match_uuid or not isinstance(match_uuid, str):
            raise ValueError("UUID матча должен быть непустой строкой")
        with self._get_session() as session:
            match = session.query(MatchORM).filter_by(uuid=match_uuid).first()
            if not match:
                logger.info(f"Матч с UUID {match_uuid} не найден")
                return None
            return self.orm_to_dto(match)

    @property
    def current_match(self):
        """Текущий матч."""
        return self._current_match

    @current_match.setter
    def current_match(self, value):
        """Установить текущий матч."""
        self._current_match = value

    def reset_current_match(self):
        """Сбросить текущий матч."""
        self._current_match = None

    # Для обратной совместимости с get_current_match()
    def get_current_match(self):
        return self._current_match