from one_relator_curvature.utils import *


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
        return self.word

    def __len__(self):
        return len(str(self))
    def cycle(self):
        next_B_index = self.word.find('B')
        current_word = self.word
        cycled_word = f"{current_word[next_B_index:]}B{current_word[:next_B_index]}"
        self.word = cycled_word[1:]
        self.inverse = word_inverse(self.word)

    def inverse_transformation(self, z):
        """ transforms point by inverse"""
        for element in reversed(self.inverse):
            matrix = self.matrices[element]
            z = mobius(matrix, z)
        return z

    def get_equivalence_class(self, generators=['a', 'b']):
        if self.equivalence_class == None:
            self.equivalence_class = equivalence_class(self.word, generators)

        return self.equivalence_class


if __name__ == '__main__':
    word = Word('ababbabbabaBBBABa', [])
    print(word.get_equivalence_class())
    word.cycle()
