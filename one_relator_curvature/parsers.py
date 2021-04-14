from argparse import ArgumentParser
from pathlib import Path


def solve_example(parser: ArgumentParser) -> None:
    """Adds arguments to parser for solving a single example"""
    parser.add_argument("--word", type=str, help="Word representing the one relator", required=True)


def solve_examples(parser: ArgumentParser) -> None:
    """adds arguments to parse for solving multiple examples"""
    parser.add_argument(
        "--word-size-range",
        type=int,
        nargs=2,
        help="range of word sizes to run examples on",
        required=True
    )

    parser.add_argument(
        "--sample-size",
        type=int,
        help="Size of sample to run on each word size",
    )


def get_polytope(parser: ArgumentParser) -> None:
    """Adds arguments to parser for outputting polytope of single example"""
    parser.add_argument("--word", type=str, help="Word representing the one relator", required=True)
    

def get_polytopes(parser: ArgumentParser) -> None:
    """
    Adds arguments to parse for outputting poltyopes for multiple examples
    """
    parser.add_argument(
        "--words", type=str, nargs="+", help="List of words to get polytopes for", required=True
    )


def get_all_cycle_data(parser: ArgumentParser) -> None:
    """Adds arguments for reading database files"""
    parser.add_argument(
        "--input-dir", type=Path, help="Directory containing database files"
    )
