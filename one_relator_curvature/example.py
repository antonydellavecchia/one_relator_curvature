from pulp import *
from hyperbolic_plane import (
    FiniteGeodesic,
    Segment,
    HyperbolicPlane
)
from circle_intersection import Geometry
from utils import mobius, get_angle
from word_utils import word_inverse
from punctured_surfaces import punctured_torus
from cell_complex import (
    CellComplex,
    ZeroCell,
    HalfEdge,
    Link
)
from results import Result
from word import Word
from errors import PrecisionError, CyclingError

from decimal import *
import copy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx
import re
from mpmath import mp, mpf, atan

class Example:
    def __init__(self, word, surface=punctured_torus):
        """
        
        """
        mobius_transformations = surface['mobius_transformations']
        self.word = Word(word[1:], mobius_transformations)
        self.fundamental_domain = surface['fundamental_domain']
        self.mobius_transformations = mobius_transformations
        self.path_start = surface['initial_point']

        self.identified_start = mobius(
            mobius_transformations['B'],
            self.path_start
        )

        # maps start point to point on B inverse side and then map by word to get endpoint
        self.path_end = self.word.transformation(self.identified_start)
        self.universal_geodesic = FiniteGeodesic(
            self.path_start,
            self.path_end
        )
        self.removed_region = None
        self.curvature = None
        self.is_valid = False
        
    def cycle_word(self):
        self.word.cycle()
        print(f"finding path end with {str(self.word)}")
        self.path_end = self.word.transformation(self.identified_start)
        self.universal_geodesic = FiniteGeodesic(self.path_start, self.path_end)

        
    def generate_segments(self):
        universal_geodesic = copy.deepcopy(self.universal_geodesic)
        segments = []
        partial_string = ''
        partial_word = Word(partial_string, self.mobius_transformations)
        segment = Segment(
            universal_geodesic,
            self.fundamental_domain,
            partial_word
        )

        segments.append(segment)
        max_segment = segment
        
        for i in reversed(self.word.inverse):
            universal_geodesic.mobius(self.word.matrices[i])
            partial_string = i + partial_string
            partial_word = Word(
                word_inverse(partial_string),
                self.mobius_transformations
            )
            segment = Segment(
                universal_geodesic,
                self.fundamental_domain,
                partial_word
            )

            if segment.absolute_max.imag > max_segment.absolute_max.imag:
                max_segment = segment

            segments.append(segment)

        self.max_segment = max_segment
        self.segments = segments

    def plot(self, fig_num=1):
        fig = plt.figure(fig_num)
        fig.suptitle(f"curvature = {self.curvature}, word = B{self.word}")
        ax = fig.add_subplot(1, 3, 3)

        if self.is_valid:
            removed_region_label = self.removed_region.label
            pos = nx.spring_layout(self.dual_graph, k=0.9)
            color_map = [
                "red" if x == removed_region_label else "blue" for x in self.dual_graph.nodes
            ]

            nx.draw(
                self.dual_graph,
                pos=pos,
                node_color=color_map,
                connectionstyle='arc3, rad = 0.1',
                ax=ax
            )
            plt.axis('off')

        hyperbolic_plane = HyperbolicPlane()
        hyperbolic_plane.tesselate(
            self.fundamental_domain,
            self.mobius_transformations.values()
        )
        hyperbolic_plane.geodesics.extend(self.segments)
        #hyperbolic_plane.geodesics.append(self.universal_geodesic)
        hyperbolic_plane.plot_upper_half(fig_num)
        hyperbolic_plane.plot_disc(fig_num)

    def generate_zero_cells(self):
        zero_cells = {}
        segments = self.segments
        number_of_segments = len(segments)
        
        for i in range(number_of_segments):
            for j in range(i+1, number_of_segments):
                radius1 = segments[i].get_radius()
                radius2 = segments[j].get_radius()
                center1 = segments[i].get_center().real
                center2 = segments[j].get_center().real
                circle1 = (center1, 0, radius1)
                circle2 = (center2, 0, radius2)

                try:
                    intersection = Geometry().circle_intersection(circle1, circle2)
                except ValueError:
                    self.is_valid = False
                    raise PrecisionError

                if intersection != None:
                    orient = segments[i].orient
                    lowerBound = segments[i].bounds[0].real * orient
                    upperBound = segments[i].bounds[1].real * orient

                    # verifies intersection is in fundamental domain
                    if lowerBound < intersection[0] * orient < upperBound:
                        z = intersection[0] + 1j * intersection[1]
                        num_zero_cells = len(zero_cells.values()) // 2
                        zero_cell = ZeroCell(segments[i], segments[j], z, num_zero_cells)
                        zero_cells[zero_cell.lifts[0]] = zero_cell
                        zero_cells[zero_cell.lifts[1]] = zero_cell

        self.zero_cells = zero_cells

    def set_sorted_lifts(self):
        # sort 0 - cell lifts in order or increasing order on the universal geodesic
        sorted_lifts = sorted(self.zero_cells, key=get_angle)
        self.sorted_lifts = list(reversed(sorted_lifts))

        # set lift index
        for lift_id, lift in enumerate(self.sorted_lifts):
            self.zero_cells[lift].set_index(lift, lift_id)
    
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
                if (start, end) in half_edges or (end, start) in half_edges.keys():
                    print("half_edge tuple already exists")                    
                    self.is_valid = False
                    raise PrecisionError()
                
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

                half_edge1 = HalfEdge(label)
                label += 1
                half_edge2 = HalfEdge(label)
                label += 1

                half_edge1.set_flip(half_edge2)
                half_edge2.set_flip(half_edge1)

                if (universal_geodesic.bounds[0], first_lift) in half_edges.keys() or \
                   (universal_geodesic.bounds[1], last_lift) in half_edges.keys():
                    print("half_edge tuple already exists")
                    self.is_valid = False
                    raise PrecisionError()
                
                half_edges[(universal_geodesic.bounds[0], first_lift)] = half_edge1
                half_edges[(universal_geodesic.bounds[1], last_lift)] = half_edge2
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
            delta_x = orientation_point.real - center.real
            delta_y = orientation_point.imag - center.imag
            index = zero_cell.get_conjugate_index(lift_tuple[1])
            
            # decimal precision
            distance_to_center = delta_x**2 + delta_y**2

            # get direction along universal geodesic 
            #if distance_to_center.compare(Decimal(radius)**2) == -1:
            comparison = distance_to_center - radius**2

            if comparison < 0:
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

    def set_regions(self):
        half_edges = self.half_edges.values()
        unique_half_edges = set([x.nxt.label for x in half_edges])
        half_edge_lables = [x.label for x in half_edges]
        half_edge_lables.sort()

        if len(unique_half_edges) != len(half_edges):
            self.is_valid = False
            raise PrecisionError()

        self.cell_complex = CellComplex(half_edges)
        self.regions = self.cell_complex.regions

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
            segment_start_phase = get_angle(segment_start - center.real)
            segment_end_phase = get_angle(segment_end - center.real)
            test_point_phase = get_angle(test_point - center.real)

            # checks if test_point lies within phase range of segment
            if segment_start_phase >= test_point_phase and segment_end_phase <= test_point_phase:
                try:
                    half_edge = half_edges[key]
                    delta_x = test_point.real - center.real
                    delta_y = test_point.imag

                    # checks if test_point lies inside semi circle or outside to determine
                    # which half edge is contained in the null region
                    if delta_x**2 + delta_y**2 - radius**2 < 0:
                        half_edge = half_edge.flip

                    # set null region
                    self.removed_region = half_edge.region

                except(KeyError):
                    self.is_valid = False
                    raise PrecisionError()

    def generate_links(self):
        label = 0
        links = []
        points = []
        for zero_cell in self.zero_cells.values():
            if (zero_cell.point in points):
                continue

            link = Link(zero_cell)
            link.full_link(label, self.removed_region)
            link.remove_stems()
            links.append(link)

            label += 1
            points.append(zero_cell.point)

        self.attaching_disc = [f"{i}disc1" for i in range(label)]
        self.attaching_disc.extend([f"{i}disc2" for i in range(label)])
        self.links = links

    def generate_cell_complex(self):
        print('generating segments')
        self.generate_segments()

        print('genera zero cells')
        self.generate_zero_cells()

        print('set sorted lifts')
        self.set_sorted_lifts()

        print('generate half edges')
        self.generate_half_edges()
        
        print('set_regions')
        self.set_regions()

        print('set removed regions')
        self.set_removed_region()

        if self.removed_region is not None:
            print("generate links")
            self.is_valid = True
            self.generate_links()

        else:
            self.is_valid = False

    def generate_dual_graph(self):
        edge_set = set()
        dual_graph = nx.MultiDiGraph()
        
        for region in self.regions:
            first_node = region.label
            target_nodes = [x.flip.region.label for x in region.half_edges]
            for node in target_nodes:
                if (node, first_node) in edge_set:
                    continue

                if (first_node, node) in edge_set:
                    dual_graph.add_edge(node, first_node)

                else:
                    dual_graph.add_edge(first_node, node)
                    
                edge_set.add((first_node, node))

        self.dual_graph = dual_graph



    def get_num_intersections(self):
        return len(self.attaching_disc) / 2

    def check_euler(self):
        euler = len(self.regions) - self.get_num_intersections()
        return euler == 0

    def find_angle_assignments(self):
        prob = LpProblem(self.word.word, LpMinimize)
        equation = ['one', 'two']
        lp_variables = {}

        for link in self.links:
            for label in link.get_labels():
                if label != 'none':
                    lp_variables[label] = LpVariable(label, 0, None, LpContinuous)

        lp_disc = [lp_variables[x] for x in self.attaching_disc]
        objective =  LpAffineExpression([(x , 1) for x in lp_disc])
        link_equations = []
        region_equations = []
        num_of_edges = 0
        
        for link in self.links:
            for equation in link.get_equations():
                link_equations.append(
                    [LpAffineExpression([(lp_variables[x] , 1) for x in equation['labels'] if x != 'none']),
                     equation['constant']]
                )

        for region in self.regions:
            num_of_edges += len(region.get_equation()) / 2

            if region.get_equation()[0] in self.removed_region.get_equation():
                print(region.get_equation(), 'removed')
                continue

            region_equations.append(
                [LpAffineExpression([(lp_variables[str(x)], 1) for x in region.get_equation()]),
                 len(region.get_equation()) - 2]
            )

        prob += objective, "minimize attaching disc"

        for equation in link_equations:
            prob += equation[0] >= equation[1]

        for equation in region_equations:
            prob += equation[0] <= equation[1]

        prob.writeLP("example_system.lp")
        prob.solve()

        self.curvature = value(prob.objective) - (len(self.attaching_disc) - 2)

        angle_labels = list(map(lambda x: x.name, prob.variables()))
        angles = list(map(lambda x: x.varValue, prob.variables()))
        self.angle_assignments = dict(zip(angle_labels, angles))

    def get_result(self):
        try:
            return Result(
                word=f"B{str(self.word)}",
                punctured_region_size=len(self.removed_region),
                intersections=self.get_num_intersections(),
                curvature=self.curvature
            )
        except TypeError:
            return None

    def run(self):
        try:
            print(f"***** running example B{self.word.word} *****")
            print('** generating cell complex **')
            self.generate_cell_complex()

        except PrecisionError:
            self.is_valid = False
            print("PrecisionError")
            return

        print("Example is valid:", self.is_valid)

        if not self.is_valid:
            return
        
        if not self.check_euler():
            self.is_valid = False
            return

        if self.removed_region is None:
            self.is_valid = False
            return
        
        self.find_angle_assignments()

        print("Example curvature:", self.curvature)

        self.is_valid = True

        print("*** generating dual graph")
        self.generate_dual_graph()

    def get_polytope(self):
        """
        return polytope of equations as an array of inequalities
        and in the form that is accepted by polymake
        """
        num_region_angles = len(self.cell_complex.half_edges)
        num_disc_angles = 2 * len(self.links)
        inequality_size = num_region_angles + num_disc_angles + 1
        inequalities = []
        disc_inequality = np.concatenate((
            [num_disc_angles - 2],
            np.zeros(num_region_angles),
            - np.ones(num_disc_angles)
        ))

        for region in self.regions:
            if region == self.removed_region:
                continue
            inequality = np.zeros(inequality_size)
            region_angles = region.get_equation()

            for index in region_angles:
                inequality[index + 1] = -1

            inequality[0] = len(region_angles) - 2
            inequalities.append(inequality)

        for link in self.links:
            for equation in link.get_equations():
                inequality = np.zeros(inequality_size)
                inequality[0] = - equation["constant"]

                for label in equation["labels"]:
                    if label != "none":
                        if "disc" in label:
                            label_integers = re.findall('\d+', label)
                            label_index = 1 + num_region_angles + int(label_integers[0]) * 2 \
                                + (int(label_integers[1]) % 2)
                            inequality[label_index] = 1
                        else:
                            inequality[1 + int(label)] = 1

                inequalities.append(inequality)

        return {
            "constraints": np.array(inequalities).tolist(),
            "disc": disc_inequality.tolist()
        }


if __name__ == '__main__':
    example = Example('BAbbAbabbABaa')
    example.run()
    
