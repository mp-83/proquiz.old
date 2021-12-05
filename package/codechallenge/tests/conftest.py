import pytest
import transaction
from codechallenge.app import StoreConfig
from codechallenge.models import Question
from codechallenge.models.meta import Base, get_engine, get_session_factory
from pyramid.config import Configurator


@pytest.fixture
def settings():
    yield {
        "sqlalchemy.url": "sqlite:///:memory:",
        "auth.secret": "sekret",
        "TEST": True,
    }


@pytest.fixture
def engine_factory(settings):
    yield get_engine(settings)


@pytest.fixture
def initTestingDB(engine_factory):
    Base.metadata.create_all(engine_factory)


@pytest.fixture
def sessionTestDB(engine_factory, initTestingDB):
    session_factory = get_session_factory(engine_factory)
    sc = StoreConfig()
    configurator = Configurator()
    configurator.registry["dbsession_factory"] = session_factory
    sc.config = configurator
    yield sc.session


@pytest.fixture
def fillTestingDB(engine_factory, sessionTestDB):
    db_session = sessionTestDB
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

    Base.metadata.drop_all(engine_factory)
