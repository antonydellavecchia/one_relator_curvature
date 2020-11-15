from typing import List
from database import session_scope
from one_relator_curvature import analysis, example, results
import matplotlib.pyplot as plt
import pandas as pd
import argparse
from one_relator_curvature.decorators import timeit

def main():
    parser = argparse.ArgumentParser(description='Process some regular sectional curvature for one relator groups')
    parser.add_argument(
        "--word-size-range",
        type=int,
        nargs="+",
        help='range of word sizes to run examples on'
    )

    args = parser.parse_args()
    word_sizes = range(*args.word_size_range)

    run_examples(word_sizes)


@timeit
def run_examples(word_sizes):
    with session_scope() as s:
        for word_size in word_sizes:
            print(f"running sample for all word size {word_size}")
            sample = analysis.Sample(word_size)
            sample.run_examples(s)


if __name__=="__main__":
    main()

    
