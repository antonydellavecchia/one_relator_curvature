from sqlalchemy import create_engine
from one_relator_curvature.results import Base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

engine = create_engine("sqlite:///examples-10-11.db")
Session = sessionmaker(bind=engine)

def recreate_database():
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
