import numpy as np
from itertools import permutations
import copy

def equivalence_class(word, generators = ['a', 'b']):
    extended_generators = copy.deepcopy(generators)
    homomorphisms = list(permutations(generators, len(generators)))
    extended_generators.extend([x.upper() for x in generators])
    equivalence_class = [word]
    
    for i in range(1, len(homomorphisms)):
        homomorphism = list(homomorphisms[i])
        homomorphism.extend([x.upper() for x in homomorphism])
        
        generator_map = dict(zip(extended_generators, homomorphism))
        letters = [generator_map[ word[i]] for i in range(len(word)) ]
        equivalence_class.append(''.join(letters))

    return equivalence_class

def inverseLetter(letter):
    if letter.isupper():
        return letter.lower()
    else:
        return letter.upper()
    
def word_inverse(word):
    inverseWord = ''

    for letter in reversed(word):
        inverseWord = inverseWord + inverseLetter(letter)
    return inverseWord


def disc_to_upper(z):
    if z == 1:
        return np.inf

    return ((z + 1) * 1j) / (1 - z)
    
def upper_to_disc(z):
    if z == np.inf:
        return 1 + 0j
    
    return (z - 1j) / (z + 1j)

def complex_to_vector(z):
    return np.array([z.real, z.imag])

def mobius(a, z):
    if z == np.inf:
        return a[0][0] * (1.0 / a[1][0])

    elif a[1][0] * z + a[1][1] == 0:
        return np.inf
    
    return (a[0][0] * z + a[0][1]) / (a[1][0] * z + a[1][1])


def get_arc(center, points):
    angles_roots = list(map(lambda x: np.angle(x - center, deg=True), points))
    angles_roots.sort()
    theta1, theta2 = angles_roots

    if abs(theta1 - theta2) > 180:
        theta2, theta1 = theta1, theta2

    return [theta1, theta2]
