from pathlib import Path
from typing import Union, List, Optional, Tuple
from example import Example
from tables import Result, Cycle
from errors import PrecisionError
from multiprocessing import Pool, cpu_count
from database import session_scope
from utils import is_passing
from word_utils import generate_all_reduced_words, get_cycles
import json


def create_example(word: str, precision=15) -> Union[None, Example]:
    """Creates and returns example if valid otheriwse returns None"""
    example = Example(word, precision)

    try:
        example.generate_inequalities()

    except PrecisionError:
        if precision < 50:
            return create_example(word, precision=precision + 10)

    if example.is_valid and example.removed_region:
        return example


def solve_example(
    word: str, print_result: bool = False, **kwargs
) -> Union[Result, None]:
    """Creates example and returns Result to be saved in database"""
    example = create_example(word)
    result = None

    if example is not None:
        example.solve()
        result = example.get_result()

    if print_result:
        if result is not None:
            print(result)
        else:
            print("Example could not be solved")

    return result


def solve_examples(
    word_size_range: List[int],
    cyclic: bool = False,
    output_dir: Optional[Path] = None,
    sample_size: int = None,
    **kwargs,
) -> None:
    if cyclic:
        raise NotImplementedError("cyclic parameter")

    if output_dir is not None:
        database_dir = output_dir / "result_databases"

    else:
        # should create a temp directory
        raise NotImplementedError("temp directory")

    for word_size in word_size_range:
        if not database_dir.exists():
            database_dir.mkdir(parents=True)

        database_path = database_dir / f"rank_2_length_{word_size}.db"
        create_all_cycles(database_path, word_size)

        with session_scope(database_path) as session:
            with Pool(cpu_count() - 1) as pool:
                print(f"running examples for word size {word_size}")
                words = ()

                if sample_size is not None:
                    raise NotImplementedError("Samples aren't implemented")
                    words = Sample(word_size, sample_size).words

                else:
                    words = generate_all_reduced_words(word_size)

                example_results = pool.map(solve_example, words)

                for example_result in example_results:
                    if example_result is not None:
                        session.merge(example_result)
                        session.commit()

    get_cycle_data(input_dir=database_dir, output_dir=output_dir, **kwargs)


def create_all_cycles(database_path: Path, word_size: int, **kwargs) -> None:
    """Initiates all cycles in the database"""
    with session_scope(database_path) as session:
        words = generate_all_reduced_words(word_size)

        for word in words:
            word_cycles = get_cycles(word)
            cycle_representative = min(word_cycles)
            session.merge(Cycle(representative_word=cycle_representative))

        session.commit()

def get_cycle_data(database_path: Path, **kwargs) -> Tuple[int, float]:
    """Returns tuple of size  and min curvature"""
    word_size = int(database_path.stem.split("_")[-1])

    with session_scope(database_path) as session:
        cycles = session.query(Cycle).all()
        passing_examples = sum(map(is_passing, cycles))
        percentage_of_passes = passing_examples / len(cycles)

    return word_size, percentage_of_passes


def get_all_cycle_data(input_dir: Path, output_dir: Path, **kwargs) -> None:
    """get data for word sequence"""
    result_tuples = []

    with Pool(cpu_count() - 1) as pool:
        databse_paths = input_dir.glob("*.db")
        result_tuples = pool.map(get_cycle_data, databse_paths)

    if output_dir is None:
        print(json.dumps(result_tuples, indent=4))

    else:
        output_results_path = output_dir / "results_array.json"

        with open(output_results_path, "w") as output_path:
            output_path.write(json.dumps(result_tuples))
