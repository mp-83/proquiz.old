from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base, TableMixin
from sqlalchemy import Column, ForeignKey, Integer, String, select
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Answer(TableMixin, Base):
    __tablename__ = "answer"

    question_uid = Column(Integer, ForeignKey("question.uid"), nullable=False)
    question = relationship("Question", back_populates="answers")
    reactions = relationship("Reaction")

    position = Column(Integer, nullable=False)
    text = Column(String(3000), nullable=False)
    __table_args__ = (UniqueConstraint("question_uid", "text"),)

    @property
    def session(self):
        return StoreConfig().session

    def all(self):
        return self.session.execute(select(Answer)).all()

    def create(self):
        self.session.add(self)
        self.session.flush()
        return self
