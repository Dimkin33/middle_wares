"""ORM-модели для работы с базой данных теннисных матчей."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class PlayerORM(Base):
    """ORM-модель игрока в теннисном турнире."""
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    matches1 = relationship(
        "MatchORM",
        back_populates="player1",
        foreign_keys="MatchORM.player1_id"
    )

    matches2 = relationship(
        "MatchORM",
        back_populates="player2",
        foreign_keys="MatchORM.player2_id"
    )



class MatchORM(Base):
    """ORM-модель матча в теннисном турнире."""
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=False)

    player1_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    winner_id = Column(Integer, ForeignKey("players.id"))

    score_str = Column(String, nullable=False)

    player1 = relationship(
        "PlayerORM",
        foreign_keys=[player1_id],
        back_populates="matches1"
    )

    player2 = relationship(
        "PlayerORM",
        foreign_keys=[player2_id],
        back_populates="matches2"
    )

    winner = relationship(
        "PlayerORM",
        foreign_keys=[winner_id]
    )




