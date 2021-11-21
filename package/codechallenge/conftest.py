import os
import pytest
import transaction
from sqlalchemy.orm import scoped_session, sessionmaker
from codechallenge.models import Base, Question, init_db, init_session


os.environ['TESTING'] = 'True'


@pytest.fixture
def initTestingDB():
    init_db()
    session = init_session()

    with transaction.manager:
        session.add_all([
            Question(text='q1.text', code='q1.code', pos=1),
            Question(text='q2.text', code='q2.code', pos=2),
            Question(text='q3.text', code='q3.code', pos=3),
        ])
        session.commit()
    return session