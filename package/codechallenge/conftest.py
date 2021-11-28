import os
import pytest
import transaction
from sqlalchemy.orm import scoped_session, sessionmaker
from codechallenge.models.meta import get_session_factory, get_engine, Base
from codechallenge.models import Question, Answer
from codechallenge.app import StoreConfig


os.environ['TESTING'] = 'True'

@pytest.fixture
def initTestingDB():
    engine = get_engine({'sqlalchemy.url': 'sqlite:///:memory:'})
    session_factory = get_session_factory(engine)
    Base.metadata.create_all(engine)
    sc = StoreConfig()
    sc.config = {'dbsession_factory': session_factory}
    db_session = sc.session

    with transaction.manager:
        db_session.add_all([
            Question(text='q1.text', code='q1.code', pos=1),
            Question(text='q2.text', code='q2.code', pos=2),
            Question(text='q3.text', code='q3.code', pos=3)
        ])
        db_session.commit()

    yield

    Base.metadata.drop_all(engine)
