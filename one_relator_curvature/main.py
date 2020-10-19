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
