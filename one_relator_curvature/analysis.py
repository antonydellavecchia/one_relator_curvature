from one_relator_curvature.hyperbolic_plane import *
from one_relator_curvature.punctured_surfaces import *
from one_relator_curvature.example import Example
from one_relator_curvature.word import Word
from one_relator_curvature.clustering import Clusters
import matplotlib.pyplot as plt
import random
from functools import reduce

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
    def __init__(self, sample_size, word_size, surface=punctured_torus, curvature_threshold=0):
        """
        
        """
        self.sample_size = sample_size
        self.curvature_threshold = curvature_threshold
        self.word_size = word_size
        self.surface = surface
        self.stats = []
        self.examples = []
        
    def generate_words(self):
        words = []
        for _ in range(self.sample_size):
            words.append(generate_word(self.word_size))

        self.words = words

    def run_examples(self):
        self.example_geodesics = []

        for word in self.words:
            word = word
            example = Example(word, curvature_threshold=self.curvature_threshold)
            example.run()

            if example.is_valid():
                self.examples.append(example)
                self.example_geodesics.append(example.universal_geodesic)

                self.stats.append([example.first_betti_number(),
                                   example.curvature,
                                   example.region_stats()
                                   ])


    def find_clusters(self, features=['curvature'], num_clusters=2):
        Clusters(self.examples).max_spacing(features, num_clusters)

    def plot(self):
        hyperbolic_plane = HyperbolicPlane()
        hyperbolic_plane.tesselate(self.surface['fundamental_domain'],
                                   self.surface['mobius_transformations'].values())
        hyperbolic_plane.geodesics.extend(self.example_geodesics)
        hyperbolic_plane.plot_upper_half()
        hyperbolic_plane.plot_disc()

        region_over_betti = list(map(lambda x: (x[0] - x[2]) / x[0], self.stats))
        curvature = list(map(lambda x: x[1], self.stats))
        cluster_groups = list(map(lambda x: x.cluster_group, self.examples))
        fig = plt.figure(3)
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(region_over_betti, curvature, c=cluster_groups)
        ax.axis([-5, 5, 0, 10])
        
        plt.show()

if __name__ == '__main__':
    sample = Sample(10, 10, curvature_threshold=0.5)
    sample.generate_words()
    sample.run_examples()
    sample.find_clusters()

    curvatures = list(map(lambda x: x.curvature , sample.examples))
    print(dict(zip(list(map(lambda x: x.word.word, sample.examples)), curvatures)))
    #refined_passed_words = set()
#
#    for passed_word in passed_words:
#        refined_passed_words = refined_passed_words.union(set(passed_word))
#
    #print(sum(map(lambda x: len(passed_word), passed_words)) - len(refined_passed_words))
    sample.plot()

