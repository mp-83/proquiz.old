from pyramid.authorization import Allow, Everyone
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register

DBSession = scoped_session(sessionmaker())
register(DBSession)
Base = declarative_base()


class Question(Base):
    __tablename__ = 'questions'
    uid = Column(Integer, primary_key=True)
    text = Column(String(200), unique=True)
    code = Column(String(5000))


class Root:
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass