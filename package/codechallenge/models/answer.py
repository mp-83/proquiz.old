from sqlalchemy import Column, Integer, ForeignKey, String, select, inspect
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship
from codechallenge.models.meta import Base
from codechallenge.app import StoreConfig


class Answer(Base):
    __tablename__ = 'answer'
    
    uid = Column(Integer, primary_key=True)
    question_uid = Column(Integer, ForeignKey('question.uid'), nullable=False)
    question = relationship('Question', back_populates='answers')
    pos = Column(Integer, nullable=False)
    text = Column(String(3000), nullable=False)
    __table_args__ = (
        UniqueConstraint('question_uid', 'text'),
    )

    @property
    def session(self):
        return StoreConfig().session

    def create(self):
        session = inspect(self).session
        session.add(self)
        session.flush()
        return self
