from pathlib import Path
from typing import Union, List
from example import Example
from tables import Result

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


def solve_example(word: str, **kwargs) -> Union[Result, None]:
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
    sample_size: int = None,
    **kwargs
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


def create_all_cycles(database_path: Path, word_size: int, **kwargs) -> None:
    """Initiates all cycles in the database"""
    with session_scope(database_path) as session:
        words = generate_all_reduced_words(word_size)

        for word in words:
            word_cycles = get_cycles(word)
            cycle_representative = min(word_cycles)
            session.merge(Cycle(representative_word=cycle_representative))

        session.commit()


def get_cycle_data(database_path: Path, **kwargs) -> None:
    """get data for word sequence"""

    with session_scope(database_path) as session:
        cycles = session.query(Cycle).all()
        passing_examples = 0

        for cycle in cycles:
            if cycle.min_curvature() < constants.EPSILON:
                passing_examples += 1

        print(passing_examples / len(cycles))

