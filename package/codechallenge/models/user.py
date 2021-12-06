import bcrypt
from codechallenge.app import StoreConfig
from codechallenge.models.meta import Base
from sqlalchemy import Column, Integer, String, select


class User(Base):
    __tablename__ = "user"
    uid = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    password_hash = Column(String)

    def set_password(self, pw):
        pwhash = bcrypt.hashpw(pw.encode("utf8"), bcrypt.gensalt())
        self.password_hash = pwhash.decode("utf8")

    def check_password(self, pw):
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode("utf8")
            return bcrypt.checkpw(pw.encode("utf8"), expected_hash)
        return False

    @property
    def session(self):
        return StoreConfig().session

    def all(self):
        return self.session.execute(select(User)).all()

    def create(self):
        self.session.add(self)
        self.session.flush()
        return self

    def save(self):
        self.session.flush()
        return self
