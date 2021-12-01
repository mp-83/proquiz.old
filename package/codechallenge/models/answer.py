from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base
from sqlalchemy import Column, ForeignKey, Integer, String, inspect, select
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Answer(Base):
    __tablename__ = "answer"

    uid = Column(Integer, primary_key=True)
    question_uid = Column(Integer, ForeignKey("question.uid"), nullable=False)
    question = relationship("Question", back_populates="answers")
    position = Column(Integer, nullable=False)
    text = Column(String(3000), nullable=False)
    __table_args__ = (UniqueConstraint("question_uid", "text"),)

    @property
    def session(self):
        return StoreConfig().session

    def all(self):
        return self.session.execute(select(Answer)).all()

    def create(self):
        session = inspect(self).session
        session.add(self)
        session.flush()
        return self
