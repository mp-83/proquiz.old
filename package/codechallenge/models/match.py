from uuid import uuid1

from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base, TableMixin
from sqlalchemy import Column, String, select
from sqlalchemy.orm import relationship


class Match(TableMixin, Base):
    __tablename__ = "match"

    name = Column(String, nullable=False, unique=True)
    games = relationship("Game")

    def __init__(self, **kwargs):
        """
        Initiate the instance

        UUID based on the host ID and current time
        the first 23 chars, are the ones based on
        the time, therefore the ones that change
        every tick and guarantee the uniqueness
        """
        _name = kwargs.get("name")
        if _name is None or _name == "":
            uuid_time_substring = "{}".format(uuid1())[:23]
            kwargs["name"] = f"M-{uuid_time_substring}"
        super().__init__(**kwargs)

    @property
    def session(self):
        return StoreConfig().session

    def create(self):
        self.session.add(self)
        self.session.flush()
        return self

    def with_name(self, name):
        matched_row = self.session.execute(select(Match).where(Match.name == name))
        return matched_row.scalar_one_or_none()

    @property
    def questions(self):
        result = []
        for g in self.games:
            result.extend(g.questions)
        return result

    @property
    def json(self):
        return {"name": self.name, "questions": [q.json for q in self.questions]}
