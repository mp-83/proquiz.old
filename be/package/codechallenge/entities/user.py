from uuid import uuid4

import bcrypt
from codechallenge.app import StoreConfig
from codechallenge.entities.meta import Base, TableMixin, classproperty
from sqlalchemy import Boolean, Column, String, select


class User(TableMixin, Base):
    __tablename__ = "user"

    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    password_hash = Column(String)
    # reactions: implicit backward relation
    # user_rankings: implicit backward relation
    private = Column(Boolean, default=False)

    def __init__(self, **kwargs):
        password = kwargs.pop("password", "")
        if password:
            self.set_password(password)
        super().__init__(**kwargs)

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

    def create(self, uhash=""):
        if not self.email and self.private:
            self.email = f"priv-{uhash}@progame.io"
        elif not self.email:
            unique_str = uuid4()
            self.email = f"pub-{unique_str}@progame.io"

        self.session.add(self)
        self.session.commit()
        return self

    def save(self):
        self.session.commit()
        return self


class Users:
    @classproperty
    def session(self):
        return StoreConfig().session

    @classmethod
    def count(cls):
        return cls.session.query(User).count()

    @classmethod
    def get_private_user(cls, mhash):
        email = f"priv-{mhash}@progame.io"
        return cls.session.query(User).filter_by(email=email).one_or_none()

    @classmethod
    def get(cls, uid):
        return cls.session.query(User).filter_by(uid=uid).one_or_none()
