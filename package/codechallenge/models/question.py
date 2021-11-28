from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import relationship
from codechallenge.models.meta import Base
from codechallenge.app import StoreConfig


class Question(Base):
    __tablename__ = 'question'

    uid = Column(Integer, primary_key=True)
    pos = Column(Integer, nullable=False)
    text = Column(String(400), nullable=False)
    code = Column(String(5000))
    answers = relationship('Answer')

    @property
    def session(self):
        config = StoreConfig().config
        factory = config['dbsession_factory']
        return factory()

    def all(self):
        return self.session.execute(select(Question)).all()

    def at_position(self, pos):
        matched_row = self.session.execute(select(Question).where(Question.pos==pos))
        return matched_row.scalar_one_or_none()

    def save(self):
        self.session.commit()
