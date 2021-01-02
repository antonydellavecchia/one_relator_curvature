from hyperbolic_plane import HyperbolicPlane
from punctured_surfaces import punctured_torus
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


def get_cycle_word_analysis(word):
    word_object = Word(word[1:])
    words = word_object.get_cyles()
    polytope_dict = {}
    results = []

    for index, example_word in enumerate(words):
        example = Example(example_word)
        example.run()
        result = example.get_result()

        if result:
            result_dict = result.__dict__
            results.append(result_dict)
            polytope_dict[example_word] =  {
                **example.get_polytope(),
                "curvature": result_dict["curvature"]
            }

        
    df_results = df.DataFrame(results)
    
    del df_results["_sa_instance_state"]

    return {
        "min_curvature": df_results["curvature"].min(),
        "max_curvature": df_results["curvature"].max(),
        "bias": 1 - (len(df_results) / len(words)),
        "polytopes": polytope_dict
    }
    
class Sample:
    def __init__(self, word_size, sample_size, surface=punctured_torus, cyclic=False): 
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
            self.surface['fundamental_domain'],
            self.surface['mobius_transformations'].values()
        )
        hyperbolic_plane.geodesics.extend(self.example_geodesics)
        hyperbolic_plane.plot_upper_half()
        hyperbolic_plane.plot_disc()

        plt.show()

if __name__ == '__main__':
    word = "BaaBAbbAbabbA"
    results = get_cycle_word_analysis(word)

    polytopes = results["polytopes"]

    with open(f"/home/antony/polytopes_{word}.json", "w") as output:
        json.dump(polytopes, output)
