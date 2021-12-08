from codechallenge.app import StoreConfig
from codechallenge.models.game import Game
from codechallenge.models.meta import Base
from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.orm import relationship


class Question(Base):
    __tablename__ = "question"

    uid = Column(Integer, primary_key=True)
    game_uid = Column(Integer, ForeignKey("game.uid"), nullable=True)
    game = relationship("Game", back_populates="questions")
    answers = relationship("Answer")
    text = Column(String(400), nullable=False)
    position = Column(Integer, nullable=False)
    code = Column(String(5000))

    def __init__(self, **kwargs):
        # To replace with db.events that aren't working now (08/12)
        if kwargs.get("game_uid") is None:
            new_game = Game(index=1).create()
            kwargs["game_uid"] = new_game.uid
        super().__init__(**kwargs)

    @property
    def session(self):
        return StoreConfig().session

    @property
    def is_open(self):
        return len(self.answers) == 0

    def all(self):
        return self.session.execute(select(Question)).all()

    def at_position(self, position):
        matched_row = self.session.execute(
            select(Question).where(Question.position == position)
        )
        return matched_row.scalar_one_or_none()

    def save(self):
        if self.position is None:
            n = self.session.query(Question).count()
            self.position = n + 1
        self.session.add(self)
        self.session.flush()
        return self

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                continue
            setattr(self, k, v)
        self.session.flush()

    @property
    def json(self):
        return {"text": self.text, "code": self.code, "position": self.position}
