from one_relator_curvature.decorators import timeit
import random
import copy
from itertools import product

def inverse_letter(letter):
    if letter.isupper():
        return letter.lower()
    else:
        return letter.upper()

def cycle_word(word):
    cycled_word = word[-1] + word[:-1]

    return cycled_word
    
def word_inverse(word):
    inverse_word = ''

    for letter in reversed(word):
        inverse_word = inverse_word + inverse_letter(letter)

    return inverse_word

def generate_random_word(size):
    word = 'B'
    letters = ['a', 'A', 'B', 'b']
    prev_char = 'B'

    for i in range(size):
        random_index = None
        if i != size - 1:
            random_index = random.randint(0, 3)
        else:
            random_index = random.randint(0, 2)
        new_char = letters[random_index]
        
        while (new_char.isupper() == prev_char.islower() or (new_char == 'b' and size - 1 == i)):
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

@timeit
def generate_all_reduced_words(size, surface_word="BAba"):
    possible_words = map(
        lambda x: "".join(x),
        product(surface_word, repeat=size)
    )

    def is_relevant(word):
        is_reduced = len(word) == len(cyclic_reduce(word))
        starts_with_B = "B" == word[0]
        multiple_letters = len(list(set(word))) > 1
        
        return is_reduced and starts_with_B and multiple_letters
        
    reduced_words = filter(
        lambda x: is_relevant(x),
        possible_words
    )

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


