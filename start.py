from database import session_scope
from one_relator_curvature import analysis, example, results
import matplotlib.pyplot as plt
import pandas as pd


def plot_intersections_curvature(data_frame, x_axis, y_axis):
    pass

def run_examples(word_sizes):
    for word_size in word_sizes:
        with session_scope() as s:
            sample = analysis.Sample(20, word_size)
            sample.generate_all_reduced_words()
            sample.run_examples(s)


if __name__=="__main__":
    with session_scope() as s:
        Result = results.Result
        statement = s.query(Result).filter(True).statement
        df = pd.read_sql(statement, s.bind)

        df.groupby("intersections")["curvature"].mean().plot()

        plt.show()
