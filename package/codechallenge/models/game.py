from codechallenge.app import StoreConfig
from codechallenge.models.match import Match
from codechallenge.models.meta import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Game(Base):
    __tablename__ = "game"

    uid = Column(Integer, primary_key=True)
    match_uid = Column(Integer, ForeignKey("match.uid"), nullable=False)
    match = relationship("Match", back_populates="games")
    questions = relationship("Question")
    index = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("match_uid", "index"),)

    def __init__(self, **kwargs):
        # To replace with db.events that aren't working now (08/12)
        if kwargs.get("match_uid") is None:
            new_match = Match().create()
            kwargs["match_uid"] = new_match.uid
        super().__init__(**kwargs)

    @property
    def session(self):
        return StoreConfig().session

    def create(self):
        self.session.add(self)
        self.session.flush()
        return self