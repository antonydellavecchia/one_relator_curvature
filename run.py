import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pulp import *
from example import Example
import random
import pandas
from collections import Counter
from hyperbolic_geometry import Word

# define mobius transformation that tile punctured torus
torus = {
    'a': [[1, 1], [1, 2]],
    'A': [[2, -1], [-1, 1]],
    'b': [[1, -1], [-1, 2]],
    'B': [[2, 1], [1, 1]]
}

def generate_csv(results, filename):
    df = pandas.DataFrame(results)

    df.to_csv(filename)
    print(df, 'csv_generated')

def results_to_csv(results, filename):
    try:
        df_csv = pandas.read_csv(filename, index_col=0)
        df_results = pandas.DataFrame(results)
        df_results = df_results.append(df_csv, ignore_index = True)
        #df_results = df_results.loc[:, ~df_results.columns.str.contains('^Unnamed')]
        df_results.to_csv(filename)
        print(df_results)
        plot_dataframe(df_results)

    except FileNotFoundError:
        generate_csv(results, filename)

def plot_dataframe(df):
    print('plotting')
    colours = {'positive': 'b', 'non-positive': 'r'}
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(
        df['length'],
        df['coord_real'],
        df['coord_imag'],
        color=[colours['positive' if r > 0.0 else 'non-positive'] for r in df['disc curvature']],
        s=60)
    ax.view_init(30, 185)
    plt.show()

def word_cancel_number(word):
    vector_word = vectorize_word(word)
    product = 1.0
    for component in vector_word:
        product *= component

    return product

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

def find_max_subword(word):
    max_sub_size = len(word)
    largest = None
    most_freq = None
    
    for i in range(1, max_sub_size - 1):
        frequencies = Counter(get_subwords(word, max_sub_size - i))
        repeated = [j for j in frequencies.values() if j > 2]
        repeated.sort()
        repeated.reverse()

        if len(repeated) > 0:
            if largest == None:
                largest = {
                    'size': max_sub_size - i,
                    'freq': repeated[0]
                }

                most_freq = largest

            if repeated[0] > most_freq['freq']:
                most_freq = {
                    'size': max_sub_size - i,
                    'freq': repeated[0]
                }   
        
    return {
        'most_freq': most_freq,
        'largest': largest
    }

def get_subwords(word, n):
    cycled_word = word
    subwords = []
    
    for letter in word:
        word = cycled_word[:n]
        subwords.append(word)

        inverse_word = Word(word, torus).inverse
        subwords.append(inverse_word)
        
        cycled_word = cycle_word(cycled_word, 1)

    print(subwords)
    return subwords

def cycle_word(word, n):
    return  word[n:] + word[:n]

def vectorize_word(word):
    vector = []
    character_map = {
        'a': 2.0,
        'A': 0.5,
        'b': 3.0,
        'B': 1.0 / 3.0
    }

    for char in word:
        vector.append(character_map[char])

    return vector

word_size = 20
words = []
disc_curvatures = []
num_removed_angles = []
num_intersect = []
lengths = []
vectors = []
word_numbers = []

def main() :
    for i in range(5):
        
        word = generate_word(word_size)
        example = None

        try:
            example = Example(word)
            #example.plot_example()

        except MemoryError:
            continue
        lp_variables = {}

        # each variable appears once in links
        for link in example.links:
            for label in link.get_labels():
                if label != 'none':
                    lp_variables[label] = LpVariable(label, 0, None, LpContinuous)

        #print(lp_variables)

        # Create the 'prob' variable to contain the problem data

        prob = LpProblem(word, LpMinimize)
        equation = ['one', 'two']
        lp_disc = [lp_variables[x] for x in example.attaching_disc]
        objective =  LpAffineExpression([(x , 1) for x in lp_disc])
        linkEquations = []

        for link in example.links:
            for equation in link.get_equations():
                linkEquations.append(
                    [LpAffineExpression([(lp_variables[x] , 1) for x in equation['labels'] if x != 'none']),
                     equation['constant']]
                )

        regionEquations = []
        num_of_edges = 0

        for region in example.regions:
            num_of_edges += len(region.get_equation()) / 2

            if region.get_equation()[0] in example.removed_region.get_equation():
                print(region.get_equation(), 'removed')
                continue

            #print(region.get_equation())
            regionEquations.append(
                [LpAffineExpression([(lp_variables[str(x)], 1) for x in region.get_equation()]),
                 len(region.get_equation()) - 2]
            )


        euler = len(example.regions) - len(example.attaching_disc) / 2

        if euler != 0:
            continue
        # The objective function
        prob += objective, "minimize attaching disc"

        for equation in linkEquations:
            prob += equation[0] >= equation[1]

        # enter region constraints
        for equation in regionEquations:
            prob += equation[0] <= equation[1]

        # The problem data is written to an .lp file
        prob.writeLP("MiracleWorker.lp")

        # The problem is solved using PuLP's choice of Solver
        prob.solve()

        print("Status:", LpStatus[prob.status])

        #for v in prob.variables():
        #    print(v.name, "=", v.varValue)

        disc_curvature = value(prob.objective) - (len(example.attaching_disc) - 2)

        words.append(word)
        disc_curvatures.append(disc_curvature)
        num_removed_angles.append(len(example.removed_region.half_edges))
        num_intersect.append(len(example.attaching_disc) / 2)
        lengths.append(example.length)
        vectors.append(vectorize_word(word))
        word_numbers.append(word_cancel_number(word))
        subword_stats = find_max_subword(word)
        most_freq = subword_stats['most_freq']
        largest = subword_stats['largest']
        coord_real = example.path_end.real
        coord_imag = example.path_end.imag * 10 ** 11
        print(coord_real, coord_imag)
        
    results = {
        'word': words,
        'disc curvature': disc_curvatures,
        '# removed angles': num_removed_angles,
        '# intersections': num_intersect,
        'length': lengths,
        'vector': vectors,
        'max subword size': largest['size'],
        'max subword freq': most_freq['freq'],
        'word cancel number': word_numbers,
        'coord_real': coord_real,
        'coord_imag': coord_imag
    }

    results_to_csv(results, 'punctured_torus_distance_examples{}.csv'.format(word_size))

