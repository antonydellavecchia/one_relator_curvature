from database import session_scope
from analysis import Sample
import argparse
from example import Example
from plotting import plot_results, plt
from word_utils import generate_all_reduced_words
from analysis import get_cycle_word_analysis
from multiprocessing import Pool


def main():
    parser = argparse.ArgumentParser(
        description='Process some regular sectional curvature for one relator groups'
    )
    parser.add_argument(
        "--word-size-range",
        type=int,
        nargs="+",
        help='range of word sizes to run examples on'
    )

    parser.add_argument(
        "--sample-size",
        type=int,
        help="Size of sample to run on each word size"
    )

    parser.add_argument('--cyclic', help="run analysis over the cycles of each word")
    
    args = parser.parse_args()

    run_examples(**vars(args))


def run_example(word):
    example = Example(word)

    example.run()
    
    if example.is_valid and example.removed_region:
        return example.get_result()
    else:
        return None


def run_examples(word_size_range, cyclic, sample_size=None):
    with session_scope() as s:
        with Pool(10) as pool:
            for word_size in word_size_range:
                print(f"running examples for word size {word_size}")
                words = ()
                
                if sample_size is not None:
                    words = Sample(word_size, sample_size).words

                else:
                    words = generate_all_reduced_words(word_size)

                if cyclic:
                    cyclic_results = pool.map(get_cycle_word_analysis, words)
                    plot_results(cyclic_results)
                    plt.show()

                else:
                    results = pool.map(run_example, words)
                            
                    for result in results:
                        if result:
                            s.add(result)

                

        s.commit()


if __name__=="__main__":
    main()

    
