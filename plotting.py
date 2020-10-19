from database import session_scope
from one_relator_curvature import results
import matplotlib.pyplot as plt
import pandas as pd

def plot_intersections_curvature(punctured_region_size):
    with session_scope() as s:
        Result = results.Result
        statement = s.query(Result).filter(Result.punctured_region_size == punctured_region_size).statement
        df = pd.read_sql(statement, s.bind)

        df.groupby("intersections")["curvature"].mean().plot()
        df.plot.scatter(x="intersections", y="curvature")
        plt.show()
