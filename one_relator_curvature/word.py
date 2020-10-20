from collections import Counter
from one_relator_curvature.utils import mobius
from one_relator_curvature.word_utils import word_inverse
from one_relator_curvature.errors import CyclingError

class Word:
    def __init__(self, word, matrices):
        """Initiate word without the leading B"""
        self.word = word
        self.matrices = matrices
        self.inverse = word_inverse(word)
        self.equivalence_class = None
        
    # transforms point by word
    def transformation(self, z):
        """transforms point by word"""
        for element in reversed(self.word):
            matrix = self.matrices[element]
            z = mobius(matrix, z)
            
        return z

    def __str__(self):
        return f"B{self.word}"

    def __len__(self):
        return len(str(self)) + 1

    def cycle(self):
        frequencies = Counter(self.word)
        print(frequencies)
        
        if frequencies["B"] > 1:
            next_B_index = self.word.find('B')
            current_word = self.word
            cycled_word = f"{current_word[next_B_index:]}B{current_word[:next_B_index]}"
            self.word = cycled_word[1:]
            self.inverse = word_inverse(self.word)

        else:
            raise CyclingError()

    def inverse_transformation(self, z):
        """ transforms point by inverse"""
        for element in reversed(self.inverse):
            matrix = self.matrices[element]
            z = mobius(matrix, z)
        return z


if __name__ == "__main__":
    word = Word("BAAAAAbbba", [[]])
    print(str(word))
    word.cycle()
    print(str(word))
