from sqlalchemy import Column, Integer, String, select
from codechallenge.models.meta import Base
from codechallenge.app import StoreConfig


class Question(Base):
    __tablename__ = 'question'

    uid = Column(Integer, primary_key=True)
    pos = Column(Integer, nullable=False)
    text = Column(String(400), nullable=False)
    code = Column(String(5000))

    @property
    def session(self):
        return

    @classmethod
    def all(cls):
        config = StoreConfig().config
        factory = config['dbsession_factory']
        session = factory()
        return session.execute(select(cls)).all()
