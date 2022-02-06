from codechallenge.app import StoreConfig
from codechallenge.entities.meta import Base, TableMixin, classproperty
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, select
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint


class Answer(TableMixin, Base):
    __tablename__ = "answer"

    question_uid = Column(Integer, ForeignKey("question.uid"), nullable=False)
    question = relationship("Question", backref="answers")
    # reactions: implicit backward relation

    position = Column(Integer, nullable=False)
    text = Column(String(3000), nullable=False)
    content_url = Column(String)
    is_correct = Column(Boolean, default=False)
    level = Column(Integer)

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

    def save(self):
        self.session.add(self)
        self.session.commit()
        return self

    def update(self, **kwargs):
        commit = kwargs.pop("commit", False)
        for k, v in kwargs.items():
            if not hasattr(self, k):
                continue
            setattr(self, k, v)

        if commit:
            self.session.commit()

    @property
    def json(self):
        return {
            "uid": self.uid,
            "text": self.text,
            "is_correct": self.is_correct,
            "position": self.position,
            "level": self.level,
            "content_url": self.content_url,
        }


class Answers:
    @classproperty
    def session(self):
        return StoreConfig().session

    @classmethod
    def count(cls):
        return cls.session.query(Answer).count()
