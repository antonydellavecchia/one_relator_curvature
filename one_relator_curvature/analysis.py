from one_relator_curvature.hyperbolic_plane import *
from one_relator_curvature.punctured_surfaces import *
from one_relator_curvature.example import Example
import matplotlib.pyplot as plt
import random

def generate_word(size):
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


class Sample:
    def __init__(self, sample_size, word_size, surface=punctured_torus):
        """

        """
        self.sample_size = sample_size
        self.word_size = word_size
        self.surface = surface

    def generate_words(self):
        words = []
        for _ in range(self.sample_size):
            words.append(generate_word(self.word_size))

        self.words = words

    def run_examples(self):
        self.example_geodesics = []

        for word in self.words:
            example = Example(word)
            example.run()

            if example.is_valid():
                self.example_geodesics.append(example.universal_geodesic)

    def plot(self):
        hyperbolic_plane = HyperbolicPlane()
        hyperbolic_plane.tesselate(self.surface['fundamental_domain'],
                                   self.surface['mobius_transformations'].values())
        hyperbolic_plane.geodesics.extend(self.example_geodesics)
        hyperbolic_plane.plot_upper_half()
        hyperbolic_plane.plot_disc()
        plt.show()

if __name__ == '__main__':
    sample = Sample(20**2, 20)
    sample.generate_words()
    sample.run_examples()
    sample.plot()
