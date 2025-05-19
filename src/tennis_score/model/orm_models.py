"""ORM-модели для работы с базой данных теннисных матчей."""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class PlayerORM(Base):
    """ORM-модель игрока в теннисном матче."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    # Обратные связи с MatchORM
    matches_as_player1 = relationship(
        "MatchORM",
        foreign_keys="MatchORM.player1_id",
        back_populates="player1"
    )
    matches_as_player2 = relationship(
        "MatchORM",
        foreign_keys="MatchORM.player2_id",
        back_populates="player2"
    )
    matches_as_winner = relationship(
        "MatchORM",
        foreign_keys="MatchORM.winner_id",
        back_populates="winner"
    )

    def __repr__(self):
        return f"<PlayerORM(id={self.id}, name='{self.name}')>"


class MatchORM(Base):
    """ORM-модель матча в теннисном турнире."""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=False)
    player1_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    winner_id = Column(Integer, ForeignKey("players.id"))
    score_str = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи с игроками
    player1 = relationship(
        "PlayerORM",
        foreign_keys=[player1_id],
        back_populates="matches_as_player1"
    )
    player2 = relationship(
        "PlayerORM",
        foreign_keys=[player2_id],
        back_populates="matches_as_player2"
    )
    winner = relationship(
        "PlayerORM",
        foreign_keys=[winner_id],
        back_populates="matches_as_winner"
    )

    def __repr__(self):
        return (
            f"<MatchORM(id={self.id}, uuid='{self.uuid}', "
            f"player1_id={self.player1_id}, player2_id={self.player2_id}, "
            f"winner_id={self.winner_id}, score='{self.score_str}')>"
        )

