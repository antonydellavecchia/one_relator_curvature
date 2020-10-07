import random
from itertools import combinations_with_replacement
from one_relator_curvature.utils import inverse_letter

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

def generate_all_words(size, surface_word="BAba"):
    possible_words = map(lambda x: "".join(x), combinations_with_replacement(surface_word, size))

def cyclic_reduce(word, surface_word="BAba"):
    generators = []
    generators[:] = surface_word
    print(generators)

if __name__ == "__main__":
    words = generate_all_words(5)
    print(list(words))

