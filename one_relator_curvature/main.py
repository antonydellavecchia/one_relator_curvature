from typing import Union
from analysis import Sample, get_cycle_word_analysis
import argparse
from example import Example
from plotting import plot_results, plt
from word_utils import generate_all_reduced_words, get_cycle_generator
from multiprocessing import Pool, cpu_count
from pathlib import Path
import json
import subprocess
from errors import PrecisionError
from functools import partial
import constants


def main():
    parser = argparse.ArgumentParser(
        description="Process some regular sectional curvature for one relator groups"
    )
    parser.add_argument(
        "--word-size",
        type=int,
        nargs="+",
        help="range of word sizes to run examples on",
    )

    parser.add_argument(
        "--sample-size", type=int, help="Size of sample to run on each word size"
    )

    parser.add_argument("--word", type=str, help="The Word representing the relation")

    parser.add_argument("--cyclic", help="run analysis over the cycles of each word")

    parser.add_argument(
        "--output-dir", type=Path, help="where to store output polytopes"
    )

    args = parser.parse_args()

    run_examples(**vars(args))


def run_cycle_examples(cycles, output_dir):
    """runs examples for all cycles"""
    cycle_analysis = {}

    for word in cycles:
        example = create_example(word, output_dir)

        if example is not None:
            # polytope_paths += [str(polytope_path)]
            #
            # polytope = example.get_polytope()
            # output_path = output_dir / f"{word}.json"

            # with open(output_path, "w") as output:
            #     json.dump(polytope, output)

            cycle_analysis[word] = example.get_result().curvature
            # polymake_call = [
        # "polymake",
        # "--script",
        # "/home/antony/projects/polymake_scripts/word_cycle_polytopes.pl",
        # *polytope_paths,
        # ]
    #
    # polymake_process = subprocess.run(polymake_call, capture_output=True)
    # cycle_analysis = json.loads(polymake_process.stdout)
    #

    num_passing_cycles = len(
        [x for x in cycle_analysis.values() if x < constants.EPSILON]
    )

    if num_passing_cycles > 0:
        return 1
    else:
        return 0


def create_example(word: str, output_dir: Path, precision=15) -> Union[None, Example]:
    example = Example(word, precision)

    try:
        example.run()

    except PrecisionError:
        if precision < 50:
            return run_example(word, output_path, precision=precision + 10)

    if example.is_valid and example.removed_region:
        return example


def run_examples(word_size_range, cyclic, output_dir, word=None, sample_size=None):
    results = {}

    for word_size in word_size_range:
        with Pool(cpu_count() - 1) as pool:
            print(f"running examples for word size {word_size}")
            words = ()

            if sample_size is not None:
                words = Sample(word_size, sample_size).words

            else:
                words = generate_all_reduced_words(word_size)

            #base_path = output_dir / f"word_size_{word_size}"
            #
            #if not base_path.exists():
                #base_path.mkdir(parents=True)

            run_cycles_partial = partial(run_cycle_examples, output_dir=output_dir)
            cycle_generator = get_cycle_generator(word_size)
            cycle_results = pool.map(run_cycles_partial, cycle_generator)

            print(
                "Percentage of passing examples:",
                sum(cycle_results) / len(cycle_results),
            )

            results[word_size] = sum(cycle_results) / len(cycle_results)
        print(results)


if __name__ == "__main__":
    main()
