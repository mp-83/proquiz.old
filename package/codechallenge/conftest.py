import os

import pytest
import transaction
from codechallenge.app import StoreConfig
from codechallenge.models import Question
from codechallenge.models.meta import Base, get_engine, get_session_factory
from pyramid.config import Configurator

os.environ["TESTING"] = "True"


@pytest.fixture
def initTestingDB():
    engine = get_engine({"sqlalchemy.url": "sqlite:///:memory:"})
    session_factory = get_session_factory(engine)
    Base.metadata.create_all(engine)
    sc = StoreConfig()
    configurator = Configurator()
    configurator.registry["dbsession_factory"] = session_factory
    sc.config = configurator
    db_session = sc.session

    with transaction.manager:
        db_session.add_all(
            [
                Question(text="q1.text", code="q1.code", position=1),
                Question(text="q2.text", code="q2.code", position=2),
                Question(text="q3.text", code="q3.code", position=3),
            ]
        )
        db_session.commit()

    yield

    Base.metadata.drop_all(engine)
