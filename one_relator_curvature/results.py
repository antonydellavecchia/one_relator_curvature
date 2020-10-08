from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True)
    intersections = Column(Integer)
    curvature = Column(Float)
    
    def __repr__(self):
        return f"<Result(word='{self.word}', intersections='{self.intersections}', curvature={self.curvature})>"

