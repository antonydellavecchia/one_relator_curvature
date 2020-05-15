from one_relator_curvature.utils import *


class Word:
    def __init__(self, word, matrices):
        self.word = word
        self.matrices = matrices
        self.inverse = word_inverse(word)
        self.equivalence_class = None
        
    # transforms point by word
    def transformation(self, z):
        for element in reversed(self.word):
            matrix = self.matrices[element]
            z = mobius(matrix, z)
            
        return z

    def __str__(self):
        return self.word

    # transform point by inverse of word
    def inverse_transformation(self, z):
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
