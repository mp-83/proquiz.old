from codechallenge.app import StoreConfig
from codechallenge.entities.meta import Base, TableMixin
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class PlayStatus(TableMixin, Base):
    __tablename__ = "play_status"

    user_id = Column(Integer, ForeignKey("user.uid"), nullable=False)
    user = relationship("User", backref="statuses")
    question_uid = Column(Integer, ForeignKey("question.uid"), nullable=False)
    game_uid = Column(Integer, ForeignKey("game.uid"), nullable=False)
    q_counter = Column(Integer)
    g_counter = Column(Integer)

    @property
    def session(self):
        return StoreConfig().session

    def refresh(self):
        self.session.refresh(self)
        return self

    def save(self):
        self.session.add(self)
        self.session.commit()
        return self
