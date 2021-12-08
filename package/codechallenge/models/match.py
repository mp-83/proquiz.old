from uuid import uuid1

from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base, TableMixin
from sqlalchemy import Column, String
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
