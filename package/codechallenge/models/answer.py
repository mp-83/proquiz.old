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
        config = StoreConfig().config
        factory = config['dbsession_factory']
        return factory()

    def create(self):
        current_session = self.session
        new_obj = current_session.merge(self)
        # import pdb;pdb.set_trace()
        current_session.add(new_obj)
        current_session.flush()
        return new_obj
