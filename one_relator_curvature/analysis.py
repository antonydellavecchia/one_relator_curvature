from one_relator_curvature.hyperbolic_plane import HyperbolicPlane
from one_relator_curvature.punctured_surfaces import punctured_torus
from one_relator_curvature.word_utils import generate_random_word, generate_all_reduced_words
from one_relator_curvature.example import Example
from one_relator_curvature.clustering import Clusters
from one_relator_curvature.errors import CyclingError
from one_relator_curvature.results import Result
import pandas as pd
import matplotlib.pyplot as plt
import random

class Sample:
    def __init__(self, sample_size, word_size, surface=punctured_torus):
        """
        
        """
        self.sample_size = sample_size
        self.word_size = word_size
        self.surface = surface
        self.examples = []

    def generate_all_reduced_words(self):
        self.words = generate_all_reduced_words(self.word_size)
        
    def generate_random_words(self):
        words = []
        for _ in range(self.sample_size):
            words.append(generate_random_word(self.word_size))

        self.words = words

    
    def run_examples(self, session):
        self.example_geodesics = []

        for word in self.words:
            word = word
            example = Example(word)
            try:
                example.run()
            
                if example.is_valid and example.removed_region:
                    example.save(session)
                    session.commit()

            except CyclingError:
                print("cycling error")

    def run_multiplication_example(self, word):
        multiplied_words = map(lambda x: word + x, self.words)

        self.run_examples(multiplied_words)
        
    def find_clusters(self, features=['curvature'], num_clusters=2):
        Clusters(self.examples).max_spacing(features, num_clusters)

    def plot(self):
        hyperbolic_plane = HyperbolicPlane()
        hyperbolic_plane.tesselate(self.surface['fundamental_domain'],
                                   self.surface['mobius_transformations'].values())
        hyperbolic_plane.geodesics.extend(self.example_geodesics)
        hyperbolic_plane.plot_upper_half()
        hyperbolic_plane.plot_disc()
        curvature = list(map(lambda x: x[1], self.stats))

        ax.axis([-5, 5, 0, 10])
        
        plt.show()

if __name__ == '__main__':
    sample = Sample(20, word_size=10)
    sample.generate_all_reduced_words()



    
