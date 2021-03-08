import json
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

    def __str__(self):
        result_dict = self.__dict__
        del result_dict["_sa_instance_state"]

        return json.dumps(result_dict, indent=4)


class Cycle(Base):
    __tablename__ = "cycles"
    representative_word = Column(String, primary_key=True)
    class_results = relationship("Result")

    def __repr__(self):
        return f"<Cycle(representative_word='{self.representative_word}')>"

    def min_curvature(self) -> float:
        try:
            min_over_cycles = min(
                (
                    result.curvature
                    for result in self.class_results
                    if result.curvature is not None
                )
            )

            return min_over_cycles

        except ValueError:
            return float("inf")
