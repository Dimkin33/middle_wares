"""ORM-модели для работы с базой данных теннисных матчей."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class PlayerORM(Base):
    """ORM-модель для хранения информации о теннисистах."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    matches1 = relationship("MatchORM", back_populates="player1", foreign_keys="MatchORM.player1_id")
    matches2 = relationship("MatchORM", back_populates="player2", foreign_keys="MatchORM.player2_id")

    def __repr__(self):
        """Строковое представление объекта PlayerORM."""
        return f"<PlayerORM(id={self.id}, name='{self.name}')>"

class MatchORM(Base):
    """ORM-модель для хранения информации о теннисных матчах."""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False, unique=True)
    player1_id = Column(Integer, ForeignKey("players.id", name="fk_match_player1"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id", name="fk_match_player2"), nullable=False)
    winner_id = Column(Integer, ForeignKey("players.id", name="fk_match_winner"))
    score_str = Column(String, nullable=False)

    player1 = relationship("PlayerORM", foreign_keys=[player1_id], back_populates="matches1")
    player2 = relationship("PlayerORM", foreign_keys=[player2_id], back_populates="matches2")
    winner = relationship("PlayerORM", foreign_keys=[winner_id])

    def __repr__(self):
        """Строковое представление объекта MatchORM."""
        return f"<MatchORM(id={self.id}, uuid='{self.uuid}', score='{self.score_str}')>"
