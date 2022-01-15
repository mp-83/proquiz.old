from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base, TableMixin
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class Ranking(TableMixin, Base):
    __tablename__ = "ranking"

    user_uid = Column(Integer, ForeignKey("user.uid"), nullable=False)
    user = relationship("User", back_populates="user_rankings")

    match_uid = Column(Integer, ForeignKey("match.uid"))
    match = relationship("Match", back_populates="rankings")

    score = Column(Integer, nullable=False)

    @property
    def session(self):
        return StoreConfig().session

    def create(self):
        self.session.add(self)
        self.session.commit()
        return self