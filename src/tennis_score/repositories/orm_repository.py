"""Репозиторий для работы с матчами и игроками через ORM (SQLite)."""
import logging
import math
from contextlib import contextmanager

from sqlalchemy import create_engine  # Удален or_
from sqlalchemy.orm import sessionmaker  # Удален aliased

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

    def _orm_to_dto_internal(self, match_orm: MatchORM, player_map: dict[int, str]) -> MatchDTO:
        """Внутренний метод для преобразования ORM-объекта матча в DTO с использованием карты игроков."""
        return MatchDTO(
            id=match_orm.id,
            uuid=match_orm.uuid,
            player1=player_map.get(match_orm.player1_id),
            player2=player_map.get(match_orm.player2_id),
            winner=player_map.get(match_orm.winner_id),
            score=match_orm.score_str,
        )

    def list_matches_paginated(
        self, page: int = 1, per_page: int = 10, filter_query: str | None = None
    ) -> tuple[list[MatchDTO], int]:
        """Получить список матчей (активных и из БД) с пагинацией и фильтрацией."""
        logger.info(f"Listing matches. Current _active_matches: {self._active_matches}") # <--- Добавлено логирование
        # 1. Get All Active Match DTOs
        active_match_dtos = [match.to_live_dto() for match in self._active_matches.values()]
        logger.info(f"Active match DTOs generated: {len(active_match_dtos)}") # <--- Добавлено логирование

        # 2. Get All DB Match DTOs
        all_db_match_dtos = []
        with self._get_session() as session:
            all_matches_orm = session.query(MatchORM).all()

            if all_matches_orm:
                player_ids_to_fetch = set()
                for m_orm in all_matches_orm:
                    if m_orm.player1_id:
                        player_ids_to_fetch.add(m_orm.player1_id)
                    if m_orm.player2_id:
                        player_ids_to_fetch.add(m_orm.player2_id)
                    if m_orm.winner_id:
                        player_ids_to_fetch.add(m_orm.winner_id)
                
                player_map = {}
                if player_ids_to_fetch:
                    players_orm = session.query(PlayerORM).filter(
                        PlayerORM.id.in_(list(player_ids_to_fetch)) # type: ignore
                    ).all()
                    player_map = {p.id: p.name for p in players_orm}

                all_db_match_dtos = [
                    self._orm_to_dto_internal(m_orm, player_map) for m_orm in all_matches_orm
                ]

        # 3. Combine All DTOs
        combined_dtos = active_match_dtos + all_db_match_dtos
        
        # 4. Filter Combined DTOs
        if filter_query:
            normalized_filter = filter_query.lower()
            filtered_dtos = [
                dto for dto in combined_dtos if (
                    (dto.player1 and normalized_filter in dto.player1.lower()) or
                    (dto.player2 and normalized_filter in dto.player2.lower())
                )
            ]
        else:
            filtered_dtos = combined_dtos

        # 5. Sort Filtered DTOs
        # Сначала активные (id is None), затем по убыванию id для сохраненных
        filtered_dtos.sort(key=lambda dto: (0 if dto.id is None else 1, -(dto.id or 0)))

        # 6. Paginate Sorted DTOs
        total_matches = len(filtered_dtos)

        if per_page > 0:
            total_pages = math.ceil(total_matches / per_page)
        else:
            total_pages = 0 if total_matches == 0 else 1 
        
        total_pages = int(max(0, total_pages))

        start_offset = (page - 1) * per_page
        end_offset = start_offset + per_page
        paginated_dtos = filtered_dtos[start_offset:end_offset]

        return paginated_dtos, total_pages

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
        logger.info(f"Current _active_matches after creation: {self._active_matches}") # <--- Добавлено логирование
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
        """Сохранить завершённый матч в БД, вернуть его DTO и удалить из активных."""
        if not match.player_one_name or not match.player_two_name:
            raise ValueError("Имена игроков не могут быть пустыми")

        player1_id = self.get_or_create_player_by_name(match.player_one_name)
        player2_id = self.get_or_create_player_by_name(match.player_two_name)
        
        if getattr(match, 'player_one_id', None) is None or getattr(match, 'player_two_id', None) is None:
            match.set_player_ids(player1_id, player2_id)
        
        winner_id = None
        if match.winner:
            if match.winner == "player1":
                winner_id = player1_id
            elif match.winner == "player2":
                winner_id = player2_id
            elif isinstance(match.winner, int) and match.winner in (player1_id, player2_id):
                winner_id = match.winner
            else:
                logger.warning(
                    f"Некорректное значение match.winner ({match.winner}) для матча {match.match_uid}. "
                    f"Победитель не будет сохранен."
                )

        self.add_match( # Убрали присваивание match_db_id
            uuid=match.match_uid,
            player1_id=player1_id,
            player2_id=player2_id,
            winner_id=winner_id,
            score=match.get_final_score_str(),
        )

        saved_match_dto = self.get_match_by_uuid_from_db(match.match_uid)

        if not saved_match_dto:
            raise RuntimeError(f"Не удалось получить DTO для сохраненного матча {match.match_uid} из БД.")

        logger.info(f"Attempting to remove match {match.match_uid} from _active_matches. Current: {self._active_matches}") # <--- Добавлено логирование
        if match.match_uid in self._active_matches:
            del self._active_matches[match.match_uid]
            logger.info(f"Активный матч {match.match_uid} удален из памяти после сохранения в БД. _active_matches: {self._active_matches}") # <--- Добавлено логирование
        else:
            logger.warning(f"Match {match.match_uid} not found in _active_matches during save_finished_match.") # <--- Добавлено логирование
        
        return saved_match_dto