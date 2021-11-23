from sqlalchemy import Column, Integer, String, select
from codechallenge.models.meta import Base, init_session


class Question(Base):
    __tablename__ = 'question'

    uid = Column(Integer, primary_key=True)
    pos = Column(Integer, nullable=False)
    text = Column(String(400), nullable=False)
    code = Column(String(5000))

    @classmethod
    def all(cls):
        session = init_session()
        return session.execute(select(cls)).all()
