from itertools import combinations
import numpy as np
from one_relator_curvature.example import Example
from networkx.utils import UnionFind as UnionFind

class Clusters:
    def __init__(self, examples):
        """

        """
        self.examples = examples
        
    def max_spacing(self, features=['curvature'], num_clusters=2):
        """
        Adds cluster group attribute to example based on features and numbe of clusters
        using max spcaing algorithm
        """
        example_pairs = list(combinations(range(len(self.examples)), 2))
        pair_dist = lambda x: self.dist(x, features)
        pair_to_edge = lambda x: [x[0], x[1], pair_dist(x)]
        edges = list(map(pair_to_edge, example_pairs))
        edges.sort(key=lambda x: x[2])
        union_find = UnionFind()
        #list(map(lambda x: union_find[x], range(len(self.examples))))
        current_num_clusters = len(self.examples)

        while current_num_clusters != num_clusters:
            edge = edges.pop(0)

            if union_find[edge[0]] != union_find[edge[1]]:
                union_find.union(edge[0], edge[1])
                current_num_clusters -= 1
            

        for (index, example) in enumerate(self.examples):
            example.cluster_group = union_find[index]

        print(list(map(lambda x: x.cluster_group, self.examples)))
    

    def dist(self, example_pair, features):
        index_to_dict = lambda x: self.examples[x].__dict__
        features_to_map = lambda y: map(lambda x: index_to_dict(y)[x], features)
        map_to_vec = lambda x: np.fromiter(features_to_map(x), dtype=float)
        feature_vectors = list(map(map_to_vec, list(example_pair)))

        return np.linalg.norm(feature_vectors[0] - feature_vectors[1])

if __name__ == "__main__":
    words = ['BabbaBBaBaa', 'BABBABABAB', 'BababaBabaa', 'Babababa']
    examples = list(map(lambda x: Example(x), words))
    run_examples = list(map(lambda x: x.run(), examples))
    
    clusters = Clusters(examples)
    clusters.max_spacing()
