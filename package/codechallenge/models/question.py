from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base
from sqlalchemy import Column, Integer, String, select
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
