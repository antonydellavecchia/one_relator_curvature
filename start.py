from typing import List
from database import session_scope
from one_relator_curvature import analysis, example, results
import matplotlib.pyplot as plt
import pandas as pd
import argparse

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        "--word-size-range",
        type=int,
        nargs="+",
        help='range of word sizes to run examples on')

    args = parser.parse_args()
    word_sizes = range(*args.word_size_range)

    run_examples(word_sizes)



def run_examples(word_sizes):
    for word_size in word_sizes:
        print(f"running sample for all word size {word_size}")
        with session_scope() as s:
            sample = analysis.Sample(20, word_size)
            sample.generate_all_reduced_words()
            sample.run_examples(s)


if __name__=="__main__":
    main()

    
