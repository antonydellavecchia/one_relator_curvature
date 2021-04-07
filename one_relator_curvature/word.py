from collections import Counter
import numpy as np

from .utils import mobius
from .word_utils import word_inverse, cycle_word, convert_to_runnable



class Word:
    def __init__(self, word, matrices=None):
        """Initiate word without the leading B"""
        self.word = word
        self.matrices = matrices
        self.inverse = word_inverse(word)
        self.equivalence_class = None
        
    # transforms point by word
    def transformation(self, z):
        """transforms point by word"""
        matrix = np.array([[1, 0], [0, 1]])
        for element in reversed(self.word):
            matrix = np.matmul(self.matrices[element], matrix)

        z = mobius(matrix, z)
            
        return z

    def __str__(self):
        return self.word

    def __len__(self):
        return len(str(self)) + 1

    def get_cycles(self):
        cycled_word = f"B{self.word}"
        cycles = {cycled_word}

        for _ in range(len(self.word)):
            cycles.add(
                convert_to_runnable(cycled_word)
            )
            cycled_word = cycle_word(cycled_word)

        return cycles

    def cycle(self):
        frequencies = Counter(self.word)
        print(frequencies)
        
        if frequencies["B"] > 1:
            word = self.word
            next_B_index = word.find('B')
            current_word = word
            cycled_word = f"{current_word[next_B_index:]}B{current_word[:next_B_index]}"
            self.word = cycled_word[1:]
            self.inverse = word_inverse(self.word)

        else:
            print("can t cycle")

    def inverse_transformation(self, z):
        """ transforms point by inverse"""
        for element in reversed(self.inverse):
            matrix = self.matrices[element]
            z = mobius(matrix, z)
        return z


if __name__ == "__main__":
    word = Word("BAAAAABa", [[]])
    word.get_cyles()

