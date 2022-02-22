from codechallenge.app import StoreConfig
from codechallenge.entities.meta import Base, TableMixin, classproperty
from sqlalchemy import Column, String, select


class OpenAnswer(TableMixin, Base):
    __tablename__ = "open_answer"

    text = Column(String(3000), nullable=False)
    content_url = Column(String)
    # reactions: implicit backward relation

    @property
    def level(self):
        return

    @property
    def session(self):
        return StoreConfig().session

    def save(self):
        self.session.add(self)
        self.session.commit()
        return self


class OpenAnswers:
    @classproperty
    def session(self):
        return StoreConfig().session

    @classmethod
    def count(cls):
        return cls.session.execute(select(OpenAnswer)).count()

    @classmethod
    def all(cls):
        return cls.session.execute(select(OpenAnswer)).all()
