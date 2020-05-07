import matplotlib.pyplot as plt
from one_relator_curvature.hyperbolic_plane import Geodesic, Domain, upper_to_disc, disc_to_upper, HyperbolicPlane, mobius
import numpy as np
import copy
from sympy import N

roots = [(np.inf,  -1.0), (-1.0, 0.0), (0.0, 1.0), (np.inf, 1.0)]
bounds = list(map(lambda x: Geodesic(x[0], x[1]), roots))
torus_fundamental_domain = Domain(bounds)

punctured_torus = {
    'fundamental_domain': torus_fundamental_domain,
    'initial_point': N(-0.5 + 0.5j, 10),
    'mobius_transformations': {
        'a': np.array([[1, 1], [1, 2]]), 
        'b': np.array([[1, -1], [-1, 2]]),
        'A': np.array([[2, -1], [-1, 1]]),
        'B': np.array([[2, 1], [1, 1]])
    }
}

roots = [(-1.8740320488976423, -1.0000000000000002),
         (-1.0000000000000002, -0.5336088038559573),
         (-0.5336088038559573, -6.123233995736766e-17), (-6.123233995736766e-17, 0.5336088038559573), (0.5336088038559573, 1.0000000000000002), (1.0000000000000002, 1.8740320488976423), (1.8740320488976423, np.inf), (np.inf, -1.8740320488976423)]

bounds = list(map(lambda x: Geodesic(x[0], x[1]), roots))
genus_2_domain = Domain(bounds)

punctured_genus_2 = {
    'fundamental_domain': genus_2_domain,
    'initial_point': 1.4370160244488213 + 0.43701602444882104 * 1j,
    'mobius_transformations': {
        'a': np.array([[ 0,  1], [-1,  3]]),
        'b': np.array([[ 0, -1], [ 1,  3]]),
        'c': np.array([[ 3, -4], [-2,  3]]),
        'd': np.array([[ 3, -2], [-4,  3]]),
        'A': np.array([[ 3., -1.], [ 1.,  0.]]),
        'B': np.array([[ 3.,  1.], [-1., -0.]]),
        'C': np.array([[3., 4.], [2., 3.]]),
        'D': np.array([[3., 2.], [4., 3.]])
    }
}
    
def find_mid_angles(angles):
    mid_angles = []

    for index, angle in enumerate(angles):
        next_index = (index + 1) % len(angles)

        if next_index == 0:
            mid_angle = np.pi 

        else:
            mid_angle = (angle + angles[next_index]) / 2
        mid_angles.append(mid_angle)

    return mid_angles

def group_adjacent_roots(roots):
    roots.sort()
    pairs = []

    for index, root in enumerate(roots):
        next_index = (index + 1) % len(roots)

        pairs.append((root, roots[next_index]))

    return pairs

def conjugate(A, g):
    return g.dot(A).dot(np.linalg.inv(g))

def push_bound(bound, matrix):
    new_bound = copy.deepcopy(bound)
    new_bound.mobius(matrix)

    return new_bound

def get_fixed_points(matrix):
    polynomial = np.array(matrix[0])
    polynomial = np.pad(polynomial, ((1, 0)))
    polynomial -= np.pad(matrix[1], ((0, 1)))

    roots = np.roots(polynomial)
    if roots.any() == np.inf:
        return np.inf

    return roots

if __name__ == '__main__':
    #roots = [(3 - np.sqrt(5)) / 2, (3 + np.sqrt(5)) / 2,
    #     (-3 - np.sqrt(5)) / 2, (-3 + np.sqrt(5)) / 2,
    #     - 1 / np.sqrt(2), 1 / np.sqrt(2),
    #     -np.sqrt(2), np.sqrt(2)]
    A = punctured_torus['mobius_transformations']['a']
    A_inv = punctured_torus['mobius_transformations']['A']
    B = punctured_torus['mobius_transformations']['b']
    B_inv = punctured_torus['mobius_transformations']['B']

    S = np.array([[0, -1], [1, 0]])
    T = np.array([[1, 1], [0, 1]])

    
    roots = np.array([get_fixed_points(A),
                      get_fixed_points(B)
    ])

    axes = list(map(lambda x: Geodesic(x[0], x[1], color='black'), roots))
    roots_disc = list(map(lambda x: upper_to_disc(x), roots.flatten()))
    roots_angles = list(map(lambda x: np.angle(x), roots_disc))
    roots_angles.sort()
    mid_angles = find_mid_angles(roots_angles)
    boundary_points_disc = list(map(lambda x: np.cos(x) + np.sin(x) * 1j, mid_angles))
    boundary_points_upper = list(map(lambda x: disc_to_upper(x).real, boundary_points_disc))
    roots = group_adjacent_roots(boundary_points_upper)
    bounds = list(map(lambda x: Geodesic(x[0], x[1]), roots))

    
    
    #points = list(map(lambda x : x.get_center() + x.get_radius() * 1j, bounds))
    #B = punctured_genus_2['mobius_transformations']['B']
    #B = first_word
    #mapped_points = list(map(lambda x: mobius(B, x), points))
    geodesics = list(map(lambda x: copy.deepcopy(x), bounds))
    new_bounds = []
    for geodesic in geodesics:
        new_bound = copy.deepcopy(geodesic)
        new_bound.mobius(B)
        new_bounds.append(new_bound)

    geodesics.extend(new_bounds)
    geodesics.extend(axes)
    #for bound in bounds:
    #    if bound.roots[1] == -1 and bound.roots[0] == np.inf:
    #        geodesics.append(bound)
    #        new_bound = push_bound(bound, B)
    #        geodesics.append(new_bound)
    #        continue
#
#        elif bound.roots[1] == 1 and bound.roots[0] == np.inf:
#            geodesics.append(bound)
#            new_bound = push_bound(bound, A)
#            geodesics.append(new_bound)
#            continue
#
#        
#        new_bounds = list(map(lambda x: push_bound(bound, x), [A, B]))
#        geodesics.extend(new_bounds)
    

    hyperbolic_plane = HyperbolicPlane()
    hyperbolic_plane.geodesics = geodesics
    #hyperbolic_plane.points = mapped_points
    #hyperbolic_plane.points.extend(points)
    hyperbolic_plane.plot_upper_half()
    hyperbolic_plane.plot_disc()
    plt.show()
