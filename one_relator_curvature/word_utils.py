import random
import copy
from itertools import product
from typing import Generator, Set


def convert_to_runnable(word, surface_word="BAba"):
    leading_letter = word[0]
    leading_index = surface_word.find(leading_letter)
    shift = len(surface_word) - leading_index
    converted_word = ""

    def new_letter(letter):
        surface_word_index = surface_word.find(letter)
        new_index = (surface_word_index + shift) % len(surface_word)

        return surface_word[new_index]

    for letter in word:
        converted_word += new_letter(letter)

    return converted_word


def inverse_letter(letter):
    if letter.isupper():
        return letter.lower()
    else:
        return letter.upper()


def cycle_word(word):
    cycled_word = word[-1] + word[:-1]

    return cycled_word


def get_cycles(word: str) -> Set[str]:
    """Returns a  of word cycles"""
    cycled_word = word
    cycles = set()
    for _ in range(len(word)):
        cycles.add(convert_to_runnable(cycled_word))
        cycled_word = cycle_word(cycled_word)

    return cycles

def word_inverse(word):
    inverse_word = ""

    for letter in reversed(word):
        inverse_word = inverse_word + inverse_letter(letter)

    return inverse_word


def generate_random_word(size):
    word = "B"
    letters = ["a", "A", "B", "b"]
    prev_char = "B"

    for i in range(size):
        random_index = None
        if i != size - 1:
            random_index = random.randint(0, 3)
        else:
            random_index = random.randint(0, 2)
        new_char = letters[random_index]

        while new_char.isupper() == prev_char.islower() or (
            new_char == "b" and size - 1 == i
        ):
            if new_char.lower() != prev_char.lower():
                break

            random_index = None
            if i != size - 1:
                random_index = random.randint(0, 3)
            else:
                random_index = random.randint(0, 2)

            new_char = letters[random_index]

        word += new_char
        prev_char = new_char
    return word


def word_generator(*alphabet, size) -> Generator[str, None, None]:
    """Returns Generator of words of given size on alphabet"""
    return map(lambda x: "".join(x), product(*alphabet, repeat=size))


def get_cycle_generator(
    size: int, surface_word="BAba"
) -> Generator[Set[str], None, None]:
    """generates all reduced cycles of a given size"""
    reduced_words = generate_all_reduced_words(size, surface_word)
    returned_cycle_representatives = set()

    for word in reduced_words:
        cycles = get_cycles(word)
        try:
            # check if cycle has already been returned
            next((cycle for cycle in cycles if cycle in returned_cycle_representatives))
        except StopIteration:
            yield get_cycles(word)

    
def generate_all_reduced_words(size, surface_word="BAba", repeat_size=6):
    num_of_sub_products = size // repeat_size
    leftover_product_size = size % repeat_size
    possible_sub_words = word_generator(surface_word, size=repeat_size)
    combinations_subwords = word_generator(possible_sub_words, size=num_of_sub_products)
    possible_leftover_subwords = word_generator(
        surface_word, size=leftover_product_size
    )
    possible_words = word_generator(
        combinations_subwords, possible_leftover_subwords, size=1
    )

    def is_relevant(word):
        is_reduced = len(word) == len(cyclic_reduce(word))
        starts_with_B = "B" == word[0]
        multiple_letters = len(set(word)) > 1

        return is_reduced and starts_with_B and multiple_letters

    reduced_words = filter(is_relevant, possible_words)

    return reduced_words


def cyclic_reduce(word, surface_word="BAba"):
    if len(word) < 2:
        return word

    generators = []
    generators[:] = surface_word
    reduced_word = copy.deepcopy(word)

    if reduced_word[-1] == inverse_letter(reduced_word[0]):
        reduced_word = reduced_word[1:-1]

    for generator in generators:
        cancellation = generator + inverse_letter(generator)
        reduced_word = reduced_word.replace(cancellation, "")

    if len(word) > len(reduced_word):
        reduced_word = cyclic_reduce(reduced_word)

    return reduced_word


if __name__ == "__main__":
    words = generate_all_reduced_words(10)
    print(len(list(words)))
