from database import session_scope
from one_relator_curvature import analysis, example, results
import matplotlib.pyplot as plt
import pandas as pd


def plot(data_frame, x_axis, y_axis):
    pass

def run_examples(session, word_size):
    sample = analysis.Sample(20, word_size)
    sample.generate_all_reduced_words()
    sample.run_examples(session)

if __name__=="__main__":
    df = None
    with session_scope() as s:
        Result = results.Result
        statement = s.query(Result).filter(Result.punctured_region_size == 2).statement
        df = pd.read_sql(statement, s.bind)

        df = df.groupby("intersections")
        df = df.first()
        print(df)
        #df.plot.scatter(x="intersections", y="curvature")
        #plt.show()
