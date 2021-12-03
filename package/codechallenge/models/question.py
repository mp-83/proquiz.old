from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base
from sqlalchemy import Column, Integer, String, inspect, select
from sqlalchemy.orm import relationship


class Question(Base):
    __tablename__ = "question"

    uid = Column(Integer, primary_key=True)
    text = Column(String(400), nullable=False)
    position = Column(Integer, nullable=False)
    code = Column(String(5000))
    answers = relationship("Answer")

    @property
    def session(self):
        return StoreConfig().session

    def all(self):
        return self.session.execute(select(Question)).all()

    def at_position(self, position):
        matched_row = self.session.execute(
            select(Question).where(Question.position == position)
        )
        return matched_row.scalar_one_or_none()

    def save(self):
        session = inspect(self).session or self.session
        session.add(self)
        session.flush()
        return self

    @property
    def json(self):
        return {"text": self.text, "code": self.code, "position": self.position}


class QuestionQuery:
    @property
    def session(self):
        return StoreConfig().session

    def all(self):
        return self.session.execute(select(Question)).all()

    def at_position(self, position):
        matched_row = self.session.execute(
            select(Question).where(Question.position == position)
        )
        return matched_row.scalar_one_or_none()
