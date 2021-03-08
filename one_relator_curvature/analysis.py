from hyperbolic_plane import HyperbolicPlane
from punctured_surfaces import get_punctured_torus
from word_utils import generate_random_word
from plotting import plot_examples, plot_results
from example import Example
from word import Word

import matplotlib.pyplot as plt
import pandas as df
from mpmath import mp
import json


def word_generator(word_size, num_of_words):
    word_number = 0

    while word_number < num_of_words:
        yield generate_random_word(word_size)
        word_number += 1


class Sample:
    def __init__(
        self, word_size, sample_size, surface=get_punctured_torus(), cyclic=False
    ):
        """
        Run a sample of randomly generated words of a given sample size
        """
        self.sample_size = sample_size
        self.word_size = word_size
        self.surface = surface
        self.words = word_generator(word_size, sample_size)
        self.cyclic = cyclic

    def get_examples(self):
        examples = []
        for word in self.words:
            example = Example(word)
            example.run()

            if example.is_valid:
                examples.append(example)

        return examples

    def get_results(self):
        results = []
        if self.cyclic:
            for word in self.words:
                analysis = get_cycle_word_analysis(word)
                results.append(analysis)

        else:
            results = [x.get_result() for x in self.get_examples()]

        return results

    def plot(self):
        # not sure if i'll need this again so i am not fixing it yet
        hyperbolic_plane = HyperbolicPlane()
        hyperbolic_plane.tesselate(
            self.surface["fundamental_domain"],
            self.surface["mobius_transformations"].values(),
        )
        hyperbolic_plane.geodesics.extend(self.example_geodesics)
        hyperbolic_plane.plot_upper_half()
        hyperbolic_plane.plot_disc()

        plt.show()

