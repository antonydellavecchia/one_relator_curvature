import matplotlib.pyplot as plt
import math as m
import cmath as c
from matplotlib import patches
from circleIntersection import *

# mobius trnasformation on a point in upper half plane
def mobius(a, z):
    return (a[0][0] * z + a[0][1]) / (a[1][0] * z + a[1][1])

# get inverse of letter
def inverseLetter(letter):
    if letter.isupper():
        return letter.lower()
    else:
        return letter.upper()
    
# return inverse of word
def word_inverse(word):
    print(word)
    inverseWord = ''

    for letter in reversed(word):
        inverseWord = inverseWord + inverseLetter(letter)
    return inverseWord

# infinite geodesics on upper half plane can be represent
# by a pair of points (point at inf := None or points on x-axis)
class Geodesic:
    def __init__(self, start, end):
        try:
            if end > start:
                self.roots = (start, end)
                self.orient = 1

            else:
                self.roots = (end, start)
                self.orient = -1

        # catch infinite geodesic
        except:
            self.roots = (start, end)
            self.orient = None

    def mobius(self, matrix):
        try:
            self.roots = tuple(map(lambda x: mobius(matrix, x), self.roots))

        # infinite case
        except:
            root1 = self.roots[0]
            root2 = self.roots[1]
            transformedRoots = []

            for i in range(2):
                if (self.roots[i] == None):
                    transformedRoots.append(matrix[0][0] * (1.0 / matrix[1][0]))

                elif (matrix[1][0] * self.roots[i] + matrix[1][1] == 0):
                    transformedRoots.append(None)

                else:
                    transformedRoots.append(
                        (matrix[0][0] * self.roots[i] + matrix[0][1])
                        / (matrix[1][0] * self.roots[i] + matrix[1][1])
                    )

            self.roots = (transformedRoots[0], transformedRoots[1])

    def get_center(self):
        return((self.roots[1] + self.roots[0]) / 2, 0.0)

    def get_radius(self):
        return abs(self.roots[1] - self.roots[0]) / 2
    
    def plot(self, ax):
        #plots half circle
        try:
            center = self.get_center()
            radius = self.get_radius()
            circ = plt.Circle(center, radius, color='g', fill=False)
            ax.add_patch(circ)

        # plots infinite line to infinity
        except:
            for i in range(2):
                if self.roots[i] == None:
                    otherRootIndex = (i + 1) % 2
                    ax.axvline(x = self.roots[otherRootIndex])
                        

class FiniteGeodesic(Geodesic):
    #all finite geodesics will lie on a semi circle
    #  we are not interested in the finite geodesics that lie
    # on an infinite line since such geodesics can only arise from
    #non reduced words
    def __init__(self, start, end):
        # Find roots of circle (center - radius), (center + radius) with center on real
        # line and passes through start, end
        center = (m.pow(abs(end), 2) - m.pow(abs(start), 2)) / (2 * (end.real - start.real))
        radius = abs(start - center)

        if start.real < end.real:
            Geodesic.__init__(self, center - radius, center + radius)
        else:
            Geodesic.__init__(self, center + radius, center - radius)

        self.bounds = (start, end)
        self.theta1 = None
        self.theta2 = None

    def mobius(self, a):
        self.roots = tuple(map(lambda x: mobius(a,x), self.roots))
        self.bounds = tuple(map(lambda x: mobius(a,x), self.bounds))
        self.setArc()
        
    def setArc(self):
        center = self.get_center()[0]
        radius = self.get_radius()

        if self.bounds[0].real < self.bounds[1].real :
            self.orient = 1
        else:
            self.orient = -1
            
        theta1 =  m.degrees(c.phase(self.bounds[0] - center))
        theta2 =  m.degrees(c.phase(self.bounds[1] - center))

        if theta1 < theta2 :
            self.theta = (theta1, theta2)
        else :
            self.theta = (theta2, theta1)
        
    def plot(self, ax):
        # inititate thetas so we can plot arc
        self.setArc()

        center = self.get_center()
        radius = self.get_radius()
        color = 'g' if self.orient == -1 else 'r'
        arc = patches.Arc(center, 2 * radius, 2 * radius, 0.0, self.theta[0], self.theta[1], color=color)
        
        # plot arc
        ax.add_patch(arc)

class Segment(FiniteGeodesic):
    # segment is a finite geodesic in the fundamental domain
    #pWord maps the segment back to a segment of the original geodesic
    def __init__(self, path, fundamental_domain, partial_word):
        self.partial_word = partial_word
        self.absolute_max = None

        # bounds are intersection
        bounds = []

        for geodesic in fundamental_domain.boundary:
            path_center = path.get_center()[0]
            path_radius = path.get_radius()

            if geodesic.roots[0] == None:
                # get x coordinate of infinite line
                x_coord = geodesic.roots[1]

                # checks for intersection
                y_squared = path_radius * path_radius - (x_coord - path_center) * (x_coord - path_center)
                if  y_squared > 0:
                    y_coord = m.sqrt(y_squared)
                    intersection = x_coord + y_coord * 1j

                    bounds.append(intersection)

            elif geodesic.roots[1] == None:
                # get x coordinate of infinite line
                x_coord = geodesic.roots[0]

                # checks for intersection
                y_squared = path_radius * path_radius - (x_coord - path_center) * (x_coord - path_center)
                if  y_squared > 0:
                    y_coord = m.sqrt(y_squared)
                    intersection = x_coord + y_coord * 1j

                    bounds.append(intersection)
            else:
                geodesic_radius = geodesic.get_radius()
                geodesic_center = geodesic.get_center()[0]
                geodesic_circle = (geodesic_center, 0, geodesic_radius)
                path_circle = (path_center, 0, path_radius)
                intersection = Geometry().circle_intersection(geodesic_circle, path_circle)

                if intersection != None:
                    intersection = intersection[0] + 1j * intersection[1]
                    bounds.append(intersection)

        # catch precision error
        if len(bounds) != 2:
            print(self.roots)
            print('error finding segment')

        else:
            FiniteGeodesic.__init__(self, bounds[0], bounds[1])

            center = self.get_center()
            radius = self.get_radius()

            # max at center
            if center[0] <= self.bounds[1].real and center[0] >= self.bounds[0].real:
                self.absolute_max = center[0] + radius * 1j

            # max at left boundary
            elif self.bounds[0].imag > self.bounds[1].imag:
                self.absolute_max = self.bounds[0].real + self.bounds[0].imag * 1j

            # max at right most boundary
            else:
                self.absolute_max = self.bounds[1].real + self.bounds[1].imag * 1j

    # lifts point on segment to universal cover
    def lift(self, point):
        return self.partial_word.transformation(point)

    # maps point on universal cover to fundamental domain
    def inverse_lift(self, point):
        return self.partial_word.inverse_transformation(point)
    
    
    
class Domain:
    def __init__(self, boundary):
        # boundary is a list of bounding geodesics
        self.boundary = boundary

    def mobius(self, matrix):
        transformedBoundary = []

        for geodesic in self.boundary:
            # create copy
            copyGeo = Geodesic(geodesic.roots[0], geodesic.roots[1])

            # transform
            copyGeo.mobius(matrix)

            # add to boundary of new domain
            transformedBoundary.append(copyGeo)

        return Domain(transformedBoundary)

    def plot(self, ax):
        for geodesic in self.boundary:
            geodesic.plot(ax)
    
    
class Word:
    def __init__(self, word, matrices):
        self.word = word
        self.matrices = matrices
        self.inverse = word_inverse(word)

    # transforms point by word
    def transformation(self, z):
        for element in reversed(self.word):
            matrix = self.matrices[element]
            z = mobius(matrix, z)
        return z

    # transform point by inverse of word
    def inverse_transformation(self, z):
        for element in reversed(self.inverse):
            matrix = self.matrices[element]
            z = mobius(matrix, z)
        return z
    
