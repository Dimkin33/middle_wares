"""Репозиторий для работы с матчами и игроками через ORM (SQLite)."""
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..dto.match_dto import MatchDTO
from ..model.match import Match
from ..model.orm_models import MatchORM, PlayerORM

# Настройка логирования
logger = logging.getLogger("orm")
logging.basicConfig(level=logging.INFO)

class OrmMatchRepository:
    """Репозиторий для работы с матчами и игроками через ORM (SQLite)."""
    def __init__(self, db_url: str = "sqlite:///tennis_score.db"):
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self._active_matches: dict[str, Match] = {} # Хранилище для активных матчей (не сохраненных в БД)

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

    def add_match(self, uuid: str, player1_id: int, player2_id: int, winner_id: int | None, score: str) -> int:  # noqa: E501
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

    def list_matches_paginated(self, page: int = 1, per_page: int = 10) -> tuple[list[MatchDTO], int]:
        import math
        """Получить список матчей с пагинацией и общее число страниц."""
        offset = (page - 1) * per_page
        with self._get_session() as session:
            total_matches = session.query(MatchORM).count()
            total_pages = math.ceil(total_matches / per_page) if per_page else 1
            matches = (
                session.query(MatchORM)
                .order_by(MatchORM.id.desc())
                .offset(offset)
                .limit(per_page)
                .all()
            )
            return [self.orm_to_dto(m) for m in matches], total_pages

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

    def orm_to_dto(self, match: MatchORM) -> MatchDTO:
        """Преобразование ORM-объекта матча в DTO с именами игроков."""
        with self._get_session() as session:
            def get_player_name(player_id: int | None) -> str | None:
                if not player_id:
                    return None
                player = session.get(PlayerORM, player_id)
                return player.name if player else None
            return MatchDTO(
                id=match.id,
                uuid=match.uuid,
                player1=get_player_name(match.player1_id),
                player2=get_player_name(match.player2_id),
                winner=get_player_name(match.winner_id),
                score=match.score_str,
            )

    def create_match(self, player_one_name: str, player_two_name: str) -> Match:
        """Создать новый объект Match и сохранить его как активный (в памяти)."""
        if not player_one_name or not player_two_name:
            raise ValueError("Имена игроков не могут быть пустыми")
        if player_one_name == player_two_name:
            raise ValueError("Игроки должны быть разными")

        match = Match(player_one_name, player_two_name)
        self._active_matches[match.match_uid] = match
        logger.info(f"Создан активный матч: {match.match_uid}, {player_one_name} vs {player_two_name}")
        return match

    def get_active_match_by_uuid(self, uuid: str) -> Match | None:
        """Получить активный (не сохраненный в БД) матч по UUID из памяти."""
        return self._active_matches.get(uuid)

    def get_match_by_uuid_from_db(self, match_uuid: str) -> MatchDTO | None:
        """Получить данные матча из БД по UUID и вернуть как MatchDTO."""
        logger.debug(f"Attempting to fetch match from DB by UUID: {match_uuid}")
        with self._get_session() as session:
            match_orm = session.query(MatchORM).filter_by(uuid=match_uuid).first()
            if match_orm:
                logger.debug(f"Match found in DB: {match_uuid}")
                return self.orm_to_dto(match_orm)
            logger.debug(f"Match with UUID {match_uuid} not found in DB.")
            return None

    def save_finished_match(self, match: Match) -> MatchDTO:
        """Сохранить завершённый матч в БД и вернуть его DTO."""
        if not match.player_one_name or not match.player_two_name:
            raise ValueError("Имена игроков не могут быть пустыми")

        player1_id = self.get_or_create_player_by_name(match.player_one_name)
        player2_id = self.get_or_create_player_by_name(match.player_two_name)
        
        # Убедимся, что ID игроков установлены в объекте Match перед сохранением
        # Это важно, если set_player_ids не был вызван ранее или был вызван с None
        if getattr(match, 'player_one_id', None) is None or getattr(match, 'player_two_id', None) is None:
            match.set_player_ids(player1_id, player2_id)
        
        # winner_id должен быть числовым ID или None
        winner_id = None
        if match.winner: # match.winner может быть player_key ("player1"/"player2") или уже ID
            if match.winner == "player1":
                winner_id = player1_id
            elif match.winner == "player2":
                winner_id = player2_id
            elif isinstance(match.winner, int) and match.winner in (player1_id, player2_id):
                winner_id = match.winner
            else: # Если match.winner это что-то неожиданное, логируем и не ставим победителя
                logger.warning(
                    f"Некорректное значение match.winner ({match.winner}) для матча {match.match_uid}. "
                    f"Победитель не будет сохранен."
                )


        match_db_id = self.add_match(
            uuid=match.match_uid,
            player1_id=player1_id,
            player2_id=player2_id,
            winner_id=winner_id, 
            score=match.get_final_score_str(),
        )
        logger.info(
            f"Матч сохранён в БД: id={match_db_id}, uuid={match.match_uid}, "
            f"{match.player_one_name} vs {match.player_two_name}"
        )
        
        # Удаляем матч из активных после сохранения
        if match.match_uid in self._active_matches:
            del self._active_matches[match.match_uid]
            logger.info(f"Матч {match.match_uid} удален из списка активных.")
            
        with self._get_session() as session:
            orm_match = session.query(MatchORM).get(match_db_id)
            return self.orm_to_dto(orm_match)