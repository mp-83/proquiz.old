from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base, TableMixin
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint


class QuestionContent(TableMixin, Base):
    __tablename__ = "question_content"

    question_uid = Column(Integer, ForeignKey("question.uid"), nullable=False)
    question = relationship("Question", back_populates="question_content")
    text = Column(String)
    url = Column(String)
    __table_args__ = (
        CheckConstraint(
            "(TEXT NOTNULL) OR (URL NOTNULL)", name="ck_question_content_text_url"
        ),
    )

    @property
    def session(self):
        return StoreConfig().session

    def create(self):
        self.session.add(self)
        self.session.commit()
        return self
