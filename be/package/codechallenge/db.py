from codechallenge.app import StoreConfig
from sqlalchemy import select


def count(cls):
    session = StoreConfig().session
    rows = session.execute(select(cls)).all()
    return len(rows)
