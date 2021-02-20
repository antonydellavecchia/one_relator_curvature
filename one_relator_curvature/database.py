from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from results import Base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from pathlib import Path


Session = sessionmaker(bind=engine)


def create_engine_from_path(database_path: Path) -> Engine:
    """Returns sqlalchemy engine at given path using sqlite"""
    return create_engine(f"sqlite:///{database_path}")



def recreate_database(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
