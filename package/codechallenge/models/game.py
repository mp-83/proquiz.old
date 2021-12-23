from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base, TableMixin
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Game(TableMixin, Base):
    __tablename__ = "game"

    match_uid = Column(Integer, ForeignKey("match.uid"), nullable=False)
    match = relationship("Match", back_populates="games")
    questions = relationship("Question")
    index = Column(Integer, default=1)
    __table_args__ = (
        UniqueConstraint("match_uid", "index", name="ck_game_match_uid_question"),
    )

    @property
    def session(self):
        return StoreConfig().session

    def create(self):
        self.session.add(self)
        self.session.flush()
        return self

    def first_question(self):
        for q in self.questions:
            if q.position == 1:
                return q

    @property
    def json(self):
        return {"index": self.index}
