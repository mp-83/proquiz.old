from sqlalchemy import Column, Integer, String, select
from codechallenge.models.meta import Base


class Answer(Base):
    __tablename__ = 'answer'
    
    uid = Column(Integer, primary_key=True)
    pos = Column(Integer, nullable=False)
    text = Column(String(3000), nullable=False)
