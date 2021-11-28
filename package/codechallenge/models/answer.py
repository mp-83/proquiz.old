from sqlalchemy import Column, Integer, ForeignKey, String, select
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
        self.session.add(self)
        self.session.flush()
        return self
