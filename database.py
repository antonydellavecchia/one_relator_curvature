from sqlalchemy import create_engine
from one_relator_curvature.results import Base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///examples.db")
Session = sessionmaker(bind=engine)

def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
