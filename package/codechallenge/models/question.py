from codechallenge.app import StoreConfig
from codechallenge.models import Answer
from codechallenge.models.game import Game
from codechallenge.models.meta import Base, TableMixin
from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.orm import relationship


class Question(TableMixin, Base):
    __tablename__ = "question"

    game_uid = Column(Integer, ForeignKey("game.uid"), nullable=True)
    game = relationship("Game", back_populates="questions")
    answers = relationship("Answer")
    reactions = relationship("Reaction")

    text = Column(String(400), nullable=False)
    position = Column(Integer, nullable=False)
    code = Column(String(5000))
    difficulty = Column(Integer)

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

    @classmethod
    def with_text(cls, text):
        session = StoreConfig().session
        matched_row = session.execute(select(cls).where(cls.text == text))
        return matched_row.scalar_one_or_none()

    def create_with_answers(self, answers):
        _answers = answers or []
        self.session.add(self)
        self.session.flush()
        for position, _answer in enumerate(_answers):
            self.session.add(
                Answer(
                    question_uid=self.uid,
                    text=_answer["text"],
                    position=position,
                    is_correct=position == 0,
                )
            )
        self.session.flush()
        return self

    @property
    def json(self):
        return {"text": self.text, "code": self.code, "position": self.position}
