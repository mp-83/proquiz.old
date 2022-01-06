from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base, TableMixin, classproperty
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, select
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Answer(TableMixin, Base):
    __tablename__ = "answer"

    question_uid = Column(Integer, ForeignKey("question.uid"), nullable=False)
    question = relationship("Question", back_populates="answers")
    reactions = relationship("Reaction")

    position = Column(Integer, nullable=False)
    text = Column(String(3000), nullable=False)
    is_correct = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("question_uid", "text"),)

    @property
    def session(self):
        return StoreConfig().session

    def all(self):
        return self.session.execute(select(Answer)).all()

    @classmethod
    def with_text(cls, text):
        session = StoreConfig().session
        matched_row = session.execute(select(cls).where(cls.text == text))
        return matched_row.scalar_one_or_none()

    def create(self):
        self.session.add(self)
        self.session.commit()
        return self


class Answers:
    @classproperty
    def session(self):
        return StoreConfig().session

    @classmethod
    def count(cls):
        return cls.session.query(Answer).count()
