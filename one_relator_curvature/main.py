from typing import Union, List
from analysis import Sample, get_cycle_word_analysis
import argparse
from example import Example
from plotting import plot_results, plt
from word_utils import generate_all_reduced_words, get_cycle_generator, get_cycles
from multiprocessing import Pool, cpu_count
from pathlib import Path
import json
import subprocess
from errors import PrecisionError
from functools import partial
from tables import Result, Cycle
import constants
from database import session_scope


def main():
    parser = argparse.ArgumentParser(
        description="Process some regular sectional curvature for one relator groups"
    )
    parser.add_argument(
        "--word-size-range",
        type=int,
        nargs="+",
        help="range of word sizes to run examples on",
    )

    parser.add_argument(
        "--sample-size", type=int, help="Size of sample to run on each word size"
    )

    # parser.add_argument("--word", type=str, help="The Word representing the relation")

    parser.add_argument("--cyclic", help="run analysis over the cycles of each word")

    parser.add_argument(
        "--database-dir", type=Path, help="Path to store database files"
    )

    args = parser.parse_args()

    run_examples(**vars(args))


def create_example(word: str, precision=15) -> Union[None, Example]:
    """Creates and returns example if valid otheriwse returns None"""
    example = Example(word, precision)

    try:
        example.run()

    except PrecisionError:
        if precision < 50:
            return create_example(word, precision=precision + 10)

    if example.is_valid and example.removed_region:
        return example


def run_example(word) -> Union[Result, None]:
    """Creates example and returns Result to be saved in database"""
    example = create_example(word)

    if example is not None:
        return example.get_result()
    else:
        return None


def run_examples(
    word_size_range: List[int],
    cyclic: bool,
    database_dir: Path,
    sample_size: int = None
) -> None:
    for word_size in word_size_range:
        if not database_dir.exists():
            database_dir.mkdir()
            
        database_path = database_dir / f"rank_2_length_{word_size}.db"
        create_all_cycles(database_path, word_size)

        with session_scope(database_path) as session:
            with Pool(cpu_count() - 2) as pool:
                print(f"running examples for word size {word_size}")
                words = ()

                if sample_size is not None:
                    words = Sample(word_size, sample_size).words

                else:
                    words = generate_all_reduced_words(word_size)

                example_results = pool.map(run_example, words)

                for example_result in example_results:
                    if example_result is not None:
                        session.merge(example_result)
                        session.commit()


def create_all_cycles(database_path: Path, word_size: int) -> None:
    """Initiates all cycles in the database"""
    with session_scope(database_path) as session:
        words = generate_all_reduced_words(word_size)

        for word in words:
            word_cycles = get_cycles(word)
            cycle_representative = min(word_cycles)
            session.merge(Cycle(representative_word=cycle_representative))

        session.commit()


def get_cycle_data(database_path: Path) -> None:
    """get data for word sequence"""

    with session_scope(database_path) as session:
        cycles = session.query(Cycle).all()
        passing_examples = 0

        for cycle in cycles:
            if cycle.min_curvature() < constants.EPSILON:
                passing_examples += 1

        print(passing_examples / len(cycles))


if __name__ == "__main__":
    main()
