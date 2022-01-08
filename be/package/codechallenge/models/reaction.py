from datetime import datetime, timezone

from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base, TableMixin, classproperty
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Reaction(TableMixin, Base):
    __tablename__ = "reaction"

    question_uid = Column(Integer, ForeignKey("question.uid"), nullable=False)
    question = relationship("Question", back_populates="reactions")
    answer_uid = Column(Integer, ForeignKey("answer.uid"), nullable=True)
    answer = relationship("Answer", back_populates="reactions")
    user_uid = Column(Integer, ForeignKey("user.uid"), nullable=False)
    user = relationship("User", back_populates="reactions")

    # used to mark reactions of a user when drops out of a match
    dirty = Column(Boolean, default=False)
    answer_time = Column(DateTime(timezone=True), nullable=True)
    score = Column(Float)

    __table_args__ = (
        UniqueConstraint("question_uid", "answer_uid", "user_uid", "create_timestamp"),
    )

    @property
    def session(self):
        return StoreConfig().session

    def create(self):
        self.session.add(self)
        self.session.commit()
        return self

    def save(self):
        self.session.add(self)
        self.session.commit()
        return self

    def record_answer(self, answer):
        self.answer = answer
        self.update_timestamp = datetime.now(tz=timezone.utc)
        self.answer_time = self.update_timestamp
        self.session.commit()
        return self

    @property
    def json(self):
        return {"text": self.text, "code": self.code, "position": self.position}


class Reactions:
    @classproperty
    def session(self):
        return StoreConfig().session

    @classmethod
    def count(cls):
        return cls.session.query(Reaction).count()

    @classmethod
    def reaction_of_user_to_question(cls, user, question):
        return (
            cls.session.query(Reaction)
            .filter_by(user=user, question=question)
            .one_or_none()
        )
