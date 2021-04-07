from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from pathlib import Path

from .tables import Base


def create_engine_from_path(database_path: Path, init=False) -> Engine:
    """Returns sqlalchemy engine at given path using sqlite"""
    engine = create_engine(f"sqlite:///{database_path}")

    if init:
        recreate_database(engine)

    return engine


def recreate_database(engine: Engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@contextmanager
def session_scope(database_path: Path, reset_db=False):
    init = not database_path.exists() or reset_db
    engine = create_engine_from_path(
        database_path,
        init=init
    )
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
