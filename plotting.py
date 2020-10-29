from database import session_scope
from one_relator_curvature.results import Result
from one_relator_curvature.word import Word
import matplotlib.pyplot as plt
import pandas as pd

def plot_intersections_curvature(punctured_region_size):
    with session_scope() as s:
        statement = s.query(Result).filter(Result.punctured_region_size == punctured_region_size).statement
        df = pd.read_sql(statement, s.bind)

        df.groupby("intersections")["curvature"].mean().plot()
        df.plot.scatter(x="intersections", y="curvature")
        plt.show()


def plot_min_cycled(words):
    with session_scope() as s:
        for word in words:
            cycled_words = Word(word[1:]).get_cyles()

            statement = s.query(Result).filter(
                Result.word.in_(cycled_words),
            ).statement

            df = pd.read_sql(statement, s.bind)
            print(df)


if __name__ == "__main__":
    plot_min_cycled(["BABABABaabA"])





