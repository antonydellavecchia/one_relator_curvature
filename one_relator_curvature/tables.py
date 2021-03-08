from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Result(Base):
    __tablename__ = "results"
    word = Column(String, primary_key=True)
    cycle_representative = Column(String, ForeignKey("cycles.representative_word"))
    punctured_region_size = Column(Integer)
    intersections = Column(Integer)
    curvature = Column(Float)

    def __repr__(self):
        return f"<Result(word='{self.word}')>"


class Cycle(Base):
    __tablename__ = "cycles"
    representative_word = Column(String, primary_key=True)
    class_results = relationship("Result")

    def __repr__(self):
        return f"<Cycle(representative_word='{self.representative_word}')>"

    def min_curvature(self) -> float:
        try:
            return min(
                (result.curvature for result in self.class_results)
            )
        except ValueError:
            return float("inf")
