import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np
import copy
from mpmath import mpf

from .circle_intersection import Geometry
from .errors import PrecisionError
from .utils import (
    mobius,
    upper_to_disc,
    complex_to_vector,
    get_arc
)


class HyperbolicPlane:
    def __init__(self):
        """
        This class stores geodesics on the hyperbolic plane
        """
        self.geodesics = []
        self.points = []

    def tesselate(
        self,
        fundamental_domain,
        mobius_transformations,
        num_iter=2
    ):
        domains = [fundamental_domain]
        iteration_number = 0

        while domains:
            domain = domains.pop()

            for transformation in mobius_transformations:
                copied_dom = copy.deepcopy(domain)
                copied_dom.mobius(transformation)
                self.geodesics.extend(copied_dom.boundary)

                if iteration_number < num_iter:
                    domains.append(copied_dom)

            iteration_number += 1

    def plot_upper_half(self, fig_num=1):
        fig = plt.figure(fig_num)
        ax = fig.add_subplot(1, 3, 1)

        for geodesic in self.geodesics:
            geodesic.plot_upper_half(ax)

        x_coords = [float(x.real) for x in self.points]
        y_coords = [float(x.imag) for x in self.points]
        ax.scatter(x_coords, y_coords)

        plt.axis([-2, 2, 0, 8])

    def plot_disc(self, fig_num = 1):
        fig = plt.figure(fig_num)
        ax = fig.add_subplot(1, 3, 2)
        circ = plt.Circle((0, 0), 1, color='black', fill=False)
        ax.add_patch(circ)

        for geodesic in self.geodesics:
            geodesic.plot_disc(ax)

        x_coords = [float(x.real) for x in self.points]
        y_coords = [float(x.imag) for x in self.points]
        ax.scatter(x_coords, y_coords)

        plt.axis([-2, 2, -2, 2])
        


class Geodesic:
    """Semi circles on upper half plane
    perpendicular circles of disc

    """
    def __init__(self, start, end, color='blue'):
        self.roots = (start, end)
        self.color = color

        if end > start:
            self.orient = 1

        else:
            self.orient = -1

        if end == float('inf') or start == float('inf'):
            self.orient = None

    def mobius(self, matrix):
        self.roots = tuple(map(lambda x: mobius(matrix, x), self.roots))

    def get_center(self):
        return sum(self.roots) / 2 + 0j

    def get_radius(self):
        return abs((self.roots[1] - self.roots[0])) / 2

    def get_roots_disc(self):
        return list(map(lambda x: upper_to_disc(x), self.roots))

    def get_center_disc(self):
        boundary_point1, boundary_point2 = list(
            map(lambda x: np.array([x.real, x.imag]), self.get_roots_disc())
        )
        
        perp_vec1, perp_vec2 = list(
            map(lambda x: np.array([-x.imag, x.real]), self.get_roots_disc())
        )
        
        if abs(np.dot(perp_vec1, perp_vec2)) == 1:
            return float("inf")

        intersection = np.dot(
            boundary_point1 - boundary_point2,
            boundary_point1
        ) / np.dot(boundary_point1, perp_vec2)

        center = np.dot(intersection, perp_vec2) + boundary_point2
        return center[0] + center[1] * 1j

    def plot_disc(self, ax):
        roots = [complex_to_vector(x) for x in self.get_roots_disc()]
        center = complex(self.get_center_disc())
        
        if center.real == float("inf"):
            x_coords = [float(x[0]) for x in roots]
            y_coords = [float(x[1]) for x in roots]
            ax.plot(x_coords, y_coords)

        else:
            roots = [complex(x) for x in self.get_roots_disc()]
            theta1, theta2 = get_arc(center, roots)
            root1 = roots[0]
            radius = float(np.linalg.norm([
                center.real - root1.real, center.imag - root1.imag
            ]))
            arc = patches.Arc(
                (center.real, center.imag),
                2 * radius, 2 * radius,
                0.0,
                float(theta1),
                float(theta2),
                color=self.color
            )
            ax.add_patch(arc)
 
    def plot_upper_half(self, ax):
        center = complex(self.get_center())
        radius = float(self.get_radius())
        
        if radius == float('inf'):
            non_inf_root = [float(x)  for x in self.roots if float(x) < float('inf')]
            ax.axvline(x=non_inf_root[0], color=self.color)

        else:
            circ = plt.Circle((center.real, center.imag), radius, color=self.color, fill=False)
            ax.add_patch(circ)

class FiniteGeodesic(Geodesic):
    def __init__(self, start, end, color='r'):
        """
        all finite geodesics will lie on a semi circle
        we are not interested in the finite geodesics that lie
        on an infinite line since such geodesics can only arise from
        non reduced words
        """
        # Find roots of circle (center - radius), (center + radius) with center on real
        # line and passes through start, end
        center = (abs(end) ** 2 - abs(start) ** 2)\
            / (2 * (end.real - start.real))
        radius = abs(start - center)

        if start.real < end.real:
            Geodesic.__init__(self, center - radius, center + radius, color)
        else:
            Geodesic.__init__(self, center + radius, center - radius, color)

        self.bounds = (start, end)
        self.theta1 = None
        self.theta2 = None

    def __str__(self):
        return f"roots: {str(self.roots)},  bounds: {str(self.bounds)}"


    def mobius(self, a):
        self.roots = tuple(map(lambda x: mobius(a, x), self.roots))
        self.bounds = tuple(map(lambda x: mobius(a, x), self.bounds))
        self.set_arc()
        
    def set_arc(self):
        center = self.get_center()

        if self.bounds[0].real < self.bounds[1].real:
            self.orient = 1
        else:
            self.orient = -1
            
        self.theta = get_arc(center, self.bounds)

    def plot_upper_half(self, ax):
        self.set_arc()
        center = complex(self.get_center())
        radius = float(self.get_radius())
        theta1, theta2 = self.theta
        arc = patches.Arc(
            (center.real, center.imag),
            2 * radius, 2 * radius,
            0.0,
            float(theta1),
            float(theta2),
            color=self.color
        )
        ax.add_patch(arc)

    def plot_disc(self, ax):
        center = complex(self.get_center_disc())
        points = [complex(upper_to_disc(x)) for x in self.bounds]
        radius = abs(center - points[0])
        theta1, theta2 = get_arc(center, points)
        arc = patches.Arc(
            (center.real, center.imag),
            2 * radius,
            2 * radius,
            0.0,
            float(theta1),
            float(theta2),
            color=self.color
        )
        ax.add_patch(arc)

        
class Segment(FiniteGeodesic):
    def __init__(self, path, fundamental_domain, partial_word):
        """ 
        segment is a finite geodesic in the fundamental domain
        pWord maps the segment back to a segment of the original geodesic
        """
        self.partial_word = partial_word
        self.absolute_max = None

        # bounds are intersection
        bounds = []
        for boundary_geodesic in fundamental_domain.boundary:
            path_center = path.get_center().real
            path_radius = path.get_radius()

            if boundary_geodesic.roots[0] == mpf("inf"):
                boundary_x = boundary_geodesic.roots[1]

                # checks for intersection
                y_squared = path_radius ** 2 - (boundary_x - path_center) ** 2
                if y_squared > 0:
                    y_coord = y_squared ** 0.5
                    intersection = boundary_x + y_coord * 1j

                    bounds.append(intersection)

            elif boundary_geodesic.roots[1] == mpf("inf"):
                boundary_x = boundary_geodesic.roots[0]

                # checks for intersection
                y_squared = path_radius ** 2 - (boundary_x - path_center) ** 2
                if y_squared > 0:
                    y_coord = y_squared ** 0.5
                    intersection = boundary_x + y_coord * 1j

                    bounds.append(intersection)
            else:
                boundary_geodesic_radius = boundary_geodesic.get_radius()
                boundary_geodesic_center = boundary_geodesic.get_center().real
                boundary_geodesic_circle = (boundary_geodesic_center, 0, boundary_geodesic_radius)
                path_circle = (path_center, 0, path_radius)
                intersection = Geometry().circle_intersection(
                    boundary_geodesic_circle,
                    path_circle
                )
                if intersection is not None:
                    intersection = intersection[0] + 1j * intersection[1]
                    bounds.append(intersection)

        # catch precision error
        if len(bounds) != 2:
            print('error finding segment')
            raise PrecisionError()

        else:
            FiniteGeodesic.__init__(self, bounds[0], bounds[1])

            center = self.get_center()
            radius = self.get_radius()

            # max at center
            if center.real <= self.bounds[1].real and \
               center.real >= self.bounds[0].real:
                self.absolute_max = center.real + radius * 1j

            # max at left boundary
            elif self.bounds[0].imag > self.bounds[1].imag:
                self.absolute_max = self.bounds[0].real + \
                    self.bounds[0].imag * 1j

            # max at right most boundary
            else:
                self.absolute_max = self.bounds[1].real + \
                    self.bounds[1].imag * 1j

    def lift(self, point):
        """lifts point on segment to universal cover"""
        return self.partial_word.transformation(point)

    def inverse_lift(self, point):
        """maps point on universal cover to fundamental domain"""
        return self.partial_word.inverse_transformation(point)


class Domain:
    def __init__(self, boundary):
        """
        takes a list of geodesics that define the fundamental domain
        in the upper half plane model
        """
        self.boundary = boundary

    def mobius(self, matrix):
        for geodesic in self.boundary:
            geodesic.mobius(matrix)

            
if __name__ == '__main__':
    roots = [(mpf("inf"),  -1.0), (-1.0, 0.0), (0.0, 1.0), (mpf("inf"), 1.0)]
    bounds = list(map(lambda x: Geodesic(x[0], x[1]), roots))
    fundamental_domain = Domain(bounds)
    hyperbolic_plane = HyperbolicPlane()

    # A, B, A inverse, B inverse
    mobius_transformations = [
        np.array([[1, 1], [1, 2]]), 
        np.array([[1, -1], [-1, 2]]), 
        np.array([[2, -1], [-1, 1]]), 
        np.array([[2, 1], [1, 1]])
    ]

    hyperbolic_plane.tesselate(fundamental_domain, mobius_transformations)
    hyperbolic_plane.plot_upper_half()
    hyperbolic_plane.plot_disc()
    plt.show()

