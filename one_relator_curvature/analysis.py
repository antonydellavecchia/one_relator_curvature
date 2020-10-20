from one_relator_curvature.hyperbolic_plane import HyperbolicPlane
from one_relator_curvature.punctured_surfaces import punctured_torus
from one_relator_curvature.word_utils import generate_random_word, generate_all_reduced_words
from one_relator_curvature.example import Example
from one_relator_curvature.clustering import Clusters
from one_relator_curvature.errors import CyclingError
from one_relator_curvature.results import Result
from one_relator_curvature.decorators import timeit

from multiprocessing import Pool
from functools import partial
import matplotlib.pyplot as plt
import random

def run_example(word):
    example = Example(word)

    try:
        example.run()
        if example.is_valid and example.removed_region:
            return example.get_result()
        else:
            return None

    except CyclingError:
        print("cycling error")
        return None

def word_generator(word_size, num_of_words):
    word_number = 0

    while word_number < num_of_words:
        yield generate_random_word(word_size)
        word_number += 1
        
    
class Sample:
    def __init__(self, word_size, surface=punctured_torus, sample_size = None):
        """
        
        """
        self.sample_size = sample_size
        self.word_size = word_size
        self.surface = surface
        self.examples = []
        
        if sample_size:
            self.words = word_generator(word_size, sample_size)
        else:
            self.words = generate_all_reduced_words(word_size)

    def run_examples(self, session = None):
        with Pool(11) as pool:
            results = pool.map(run_example, self.words)
            
            for result in results:
                if result:
                    session.add(result)

        session.commit()
        
    def plot(self):
        hyperbolic_plane = HyperbolicPlane()
        hyperbolic_plane.tesselate(
            self.surface['fundamental_domain'],
            self.surface['mobius_transformations'].values()
        )
        hyperbolic_plane.geodesics.extend(self.example_geodesics)
        hyperbolic_plane.plot_upper_half()
        hyperbolic_plane.plot_disc()
        curvature = list(map(lambda x: x[1], self.stats))

        ax.axis([-5, 5, 0, 10])
        
        plt.show()

if __name__ == '__main__':
    sample = Sample(11)
    sample.run_examples()




    
