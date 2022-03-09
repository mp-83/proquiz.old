from hashlib import blake2b
from uuid import uuid4

import bcrypt
from codechallenge.app import StoreConfig
from codechallenge.entities.meta import Base, TableMixin, classproperty
from sqlalchemy import Column, String, select
from sqlalchemy.ext.hybrid import hybrid_property


class UserFactory:
    def __init__(self, **kwargs):
        self.original_email = kwargs.pop("original_email", "")
        self.signed = kwargs.pop("signed", None) or self.original_email
        self.kwargs = kwargs

    def fetch(self):
        email = self.kwargs.get("email")
        if email:
            user = Users.get_2(email)
            return user or User(**self.kwargs).save()

        key = uuid4().hex.encode("utf-8")
        h = blake2b(key=key, digest_size=16)
        h.update(self.original_email.encode("utf-8"))
        digest = h.hexdigest()
        email = f"{digest}@progame.io"

        user = Users.get_2(email)
        if user:
            return user

        if not self.signed:
            unique_str = uuid4().hex
            email = f"uns-{unique_str}@progame.io"
            return User(email=email).save()

        user = User()
        user.key = key
        user.email = email
        user.digest = digest
        user.save()
        return user


class User(TableMixin, Base):
    __tablename__ = "user"

    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    password_hash = Column(String)
    # reactions: implicit backward relation
    # user_rankings: implicit backward relation
    key = Column(String)
    digest = Column(String)

    def __init__(self, **kwargs):
        password = kwargs.pop("password", None)
        if password:
            self.set_password(password)

        super().__init__(**kwargs)

    @hybrid_property
    def signed(self):
        return self.digest is not None

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

    def save(self):
        self.session.add(self)
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
    def get_2(cls, email):
        return cls.session.query(User).filter_by(email=email).one_or_none()

    @classmethod
    def get(cls, uid):
        return cls.session.query(User).filter_by(uid=uid).one_or_none()
