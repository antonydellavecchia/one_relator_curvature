import matplotlib.pyplot as plt
from hyperbolic_geometry import *
from cell_complex import *
import cmath as c
import math
from decimal import *
from mpmath import *

A = [[1, 1], [1, 2]]
Ainv = [[2, -1], [-1, 1]]
B = [[1, -1], [-1, 2]]
Binv = [[2, 1], [1, 1]]
mobT = [A, B, Ainv, Binv]
iterations = 6

# fundamental domain of punctured torus
bound1 = Geodesic(None,  -1.0)
bound2 =  Geodesic(-1.0, 0.0)
bound3 = Geodesic(0.0, 1.0)
bound4 = Geodesic(None, 1.0)
boundary = [bound1, bound2, bound3, bound4]
torus_fun_dom = Domain(boundary)

# define mobius transformation that tile punctured torus
torus = {
    'a': [[1, 1], [1, 2]],
    'A': [[2, -1], [-1, 1]],
    'b': [[1, -1], [-1, 2]],
    'B': [[2, 1], [1, 1]]
}

# tesselate upper half plane
def tesselate(dom, ax, prevT, i):
    iterations = 6

    # plot current dom
    dom.plot(ax)
    
    # base case
    if i == iterations:
        pass

    # apply all possible mobius transformations
    elif i == 0:
        for j in range(4):
            transformedDom = dom.mobius(mobT[j])
            tesselate(transformedDom, ax, j, i + 1)

    # apply all mobius transformations except inverse previous
    else:
        t1 = prevT
        t2 = (prevT + 1) % 4
        t3 = (t2 + 2) % 4
        possibleTransformations = [t1, t2, t3]

        for j in possibleTransformations:
            transformedDom = dom.mobius(mobT[j])
            tesselate(transformedDom, ax, j, i + 1)


# defines an exampl of a geodesic on a surface 
class Example:
    def __init__(self, word):
        # run example on punctured torus for now
        self.fundamental_domain = torus_fun_dom

        # create word object from word string, word should start with B
        self.word = Word(word, torus)
    
        # run example starting from a point on B side
        mp.dps = 30
        path_start = mpc(-0.5, 0.5)
        self.path_start = path_start

        # maps start point to point on B inverse side and then map by word to get endpoint
        path_end = mobius(Binv, path_start)
        path_end = self.word.transformation(path_end)
        
        self.path_end = mpc(path_end.real, path_end.imag)

        #map to geodesic to disc model
        print(self.path_end)
        endpoint = (self.path_end - self.path_start) / (self.path_end - mpc(-0.5, 0.5))
        self.endpoint = endpoint
        
        # calculate hyperbolic length
        print(mp.polar(endpoint))
        self.length = math.log((1 + polar(endpoint)[0]) / (1 - polar(endpoint)[0]))

        # create path on universal cover
        self.universal_geodesic = FiniteGeodesic(path_start, path_end)
       
        # plot and store segments
        self.generate_segments()
#
        # set dict of ZeroCells, keys are lifts of intersections on fundamental domain
        self.generate_zero_cells()

        # set sortd lifts and index the zero cells accordingly
        self.set_sorted_lifts()
        
        # reset universal geodesic
        self.universal_geodesic = FiniteGeodesic(path_start, path_end)
    
        # generate halfedges
        self.generate_half_edges()

        # create cell complex
        self.regions = CellComplex(self.half_edges.values()).regions
                
        # set region to be removed
        self.set_removed_region()
                
        # generate links
        label = 0
        links = []
        points = []
        for zero_cell in self.zero_cells.values():
            if (zero_cell.point in points):
                continue


            link = Link()
            link.full_link(zero_cell, label, self.removed_region)
            link.remove_stems()
            links.append(link)

            label += 1
            points.append(zero_cell.point)
            print(zero_cell.point)

        self.attaching_disc = ['{}disc1'.format(i) for i in range(label)]
        self.attaching_disc.extend(['{}disc2'.format(i) for i in range(label)])

        self.links = links

    # generate segments and set max segment
    def generate_segments(self):
        # initite list of segments
        segments = []

        # word that maps segment to originally position on universal Geodesic
        partial_string = ''
        partial_word = Word(partial_string, torus)
    
        # segment of universal geodesic
        segment = Segment(self.universal_geodesic, self.fundamental_domain, partial_word)
        segments.append(segment)

        # segment with largest absolute max
        max_segment = segment

        for i in reversed(self.word.inverse):
            # map universal geodesic back one letter at a time
            # to segment it on the fundamental domain
            self.universal_geodesic.mobius(self.word.matrices[i])

            partial_string = i + partial_string
            partial_word = Word(word_inverse(partial_string), torus)
            segment = Segment(self.universal_geodesic, self.fundamental_domain, partial_word)

            if segment.absolute_max.imag > max_segment.absolute_max.imag:
                max_segment = segment

            segments.append(segment)


        # max segment containes maximum point over all segments
        self.max_segment = max_segment

        # sets segmnts
        self.segments = segments

    def plot_example(self):
        ## inititate plot
        fig = plt.figure()
    
        # define axes
        ax = fig.add_subplot(1, 1, 1)
        plt.axis([-2, 2, 0, 2])

        # draws tesselation up to some predefined iteration
        tesselate(self.fundamental_domain, ax, 0, 0)

        #plot universal_geodesic
        self.universal_geodesic.plot(ax)


        for segment in self.segments:
            segment.plot(ax)

        # show plot
        plt.show()


    def generate_zero_cells(self):
        # intersections insie fundamental domain
        # indexed by lifts of intersections to universal cover
        zero_cells  = {}
        segments = self.segments
        number_of_segments = len(segments)
        
        for i in range(number_of_segments):
            for j in range(i+1, number_of_segments):
                radius1 = segments[i].get_radius()
                radius2 = segments[j].get_radius()
                center1 = segments[i].get_center()[0]
                center2 = segments[j].get_center()[0]
                circle1 = (center1, 0, radius1)
                circle2 = (center2, 0, radius2)
                intersection = Geometry().circle_intersection(circle1, circle2)

                if intersection != None:
                    orient = segments[i].orient
                    lowerBound = segments[i].bounds[0].real * orient
                    upperBound = segments[i].bounds[1].real * orient

                    # verifies intersection is in fundamental domain
                    if lowerBound < intersection[0] * orient < upperBound:
                        z = intersection[0] + 1j * intersection[1]
                        zero_cell = ZeroCell(segments[i], segments[j], z)
                        zero_cells[zero_cell.lifts[0]] = zero_cell
                        zero_cells[zero_cell.lifts[1]] = zero_cell

        self.zero_cells = zero_cells

    def set_sorted_lifts(self):
        # sort 0 - cell lifts in order or increasing order on the universal geodesic
        sorted_lifts = sorted(self.zero_cells, key = lambda key: c.phase(key))
        self.sorted_lifts = list(reversed(sorted_lifts))

        # set lift index
        for lift_id, lift in enumerate(self.sorted_lifts):
            self.zero_cells[lift].set_index(lift, lift_id)
    

    # half edges are pointed egdes of cell comples (1 - cells)
    # they start and end at a zero-cell
    def generate_half_edges(self):
        ### initiate halfedges and their flips ###
        label = 0
        half_edges = {}
        sorted_lifts = self.sorted_lifts
        zero_cells = self.zero_cells
        universal_geodesic = self.universal_geodesic
        
        for lift_id, lift in enumerate(sorted_lifts):
            if lift_id + 1 < len(sorted_lifts):
                start = lift
                end = sorted_lifts[lift_id + 1]

                # create half edge
                half_edge1 = HalfEdge(label)
                label += 1

                # create flip
                half_edge2 = HalfEdge(label)
                label += 1

                # set respective flips
                half_edge1.set_flip(half_edge2)
                half_edge2.set_flip(half_edge1)

                # add to dict
                half_edges[(start, end)] = half_edge1
                half_edges[(end, start)] = half_edge2

                # add halfedges that point to zero-cell
                zero_cells[end].half_edges.append(half_edge1)
                zero_cells[start].half_edges.append(half_edge2)

            # deal with half edge between first and last lift
            else:
                last_lift = lift
                first_lift = sorted_lifts[0]
                start_zero_cell = zero_cells[first_lift]
                end_zero_cell = zero_cells[last_lift]
            
                # create half edge
                half_edge1 = HalfEdge(label)
                label += 1

                # create flip
                half_edge2 = HalfEdge(label)
                label += 1

                # set respective
                half_edge1.set_flip(half_edge2)
                half_edge2.set_flip(half_edge1)

                # add to dict
                half_edges[(universal_geodesic.bounds[0], first_lift)] = half_edge1
                half_edges[(universal_geodesic.bounds[1], last_lift)] = half_edge2

                # add halfedges that point to zero-cell
                start_zero_cell.half_edges.append(half_edge1)
                end_zero_cell.half_edges.append(half_edge2)



        # set the next half edges 
        for lift_tuple in half_edges.keys():
            half_edge = half_edges[lift_tuple]
            zero_cell = zero_cells[lift_tuple[1]]

            # map half edge endpoint near opposite lif of start point
            orientation_point = zero_cell.switch_lift(lift_tuple[1], lift_tuple[0])

            center = universal_geodesic.get_center()
            radius = universal_geodesic.get_radius()
            delta_x = orientation_point.real - center[0]
            delta_y = orientation_point.imag - center[1]
            index = zero_cell.get_conjugate_index(lift_tuple[1])
            
            # decimal precision
            getcontext().prec = 100
            distance_to_center = delta_x**2 + delta_y**2

            # get direction along universal geodesic 
            if distance_to_center.compare(Decimal(radius)**2) == -1:
                next_index = index - 1
            
            else:
                next_index = index + 1

            # find next halfedge
            if next_index == -1:
                next_index = len(sorted_lifts) - 1
                next_half_edge = half_edges[(universal_geodesic.bounds[1], sorted_lifts[next_index])]
            
            elif next_index == len(sorted_lifts):
                next_index = 0
                next_half_edge = half_edges[(universal_geodesic.bounds[0], sorted_lifts[next_index])]

            else:
                next_half_edge = half_edges[(sorted_lifts[index], sorted_lifts[next_index])]
                                
            half_edge.set_next(next_half_edge)


        self.half_edges = half_edges

    # removes region that contains point at infinity
    def set_removed_region(self):
        universal_geodesic = self.universal_geodesic
        zero_cells = self.zero_cells
        half_edges = self.half_edges
        max_segment = self.max_segment
        sorted_lifts = self.sorted_lifts
        center = universal_geodesic.get_center()
        radius = universal_geodesic.get_radius()

        # points used to verify which half edge is contained in puncture region
        test_point = max_segment.lift(max_segment.absolute_max + 1j)

        # find half edge closest to test point
        for i in range(len(sorted_lifts)):
            segment_start = sorted_lifts[i]

            # get end bound if last segment
            if i + 1 == len(sorted_lifts):
                segment_end = universal_geodesic.bounds[1]

            else:
                segment_end = sorted_lifts[i + 1]

            
            key = (segment_start, segment_end)

            # center has no imag part
            segment_start_phase = c.phase(segment_start - center[0])
            segment_end_phase = c.phase(segment_end - center[0])
            test_point_phase = c.phase(test_point - center[0])

            # checks if test_point lies within phase range of segment
            if segment_start_phase >= test_point_phase and segment_end_phase <= test_point_phase:
                half_edge = half_edges[key]
                delta_x = test_point.real - center[0]
                delta_y = test_point.imag

                # checks if test_point lies inside semi circle or outside to determine
                # which half edge is contained in the null region
                if (Decimal(delta_x)**2 + Decimal(delta_y)**2).compare(Decimal(radius)**2) == -1:
                    half_edge = half_edge.flip

                # set null region
                self.removed_region = half_edge.region
