from .utils import get_angle


class ZeroCell:
    def __init__(self, segment1, segment2, point, label):
        """
         0 - cells that arise from an intersection of segments
        hence the point lies in the fundamental domain
        they can also be identified by the list of halfedges that point to them
        """
        self.label = label
        self.point = point
        self.index = (None, None)
        self.half_edges = []

        # lifts of intersection points to universal cover
        lift1 = segment1.lift(point)
        lift2 = segment2.lift(point)

        # order segments by order of appearance while follow geodesic in universal
        # cover starting from point in fundamental domain
        if get_angle(lift1) > get_angle(lift2):
            self.lifts = (lift1, lift2)
            self.segments = (segment1, segment2)

        else:
            self.lifts = (lift2, lift1)
            self.segments = (segment2, segment1)

    def switch_lift(self, lift, point):
        """
        maps point near lift in universal cover
        line between lift and point represent a one cell in universal cover
        we map down to fundamental domain and map to the other lift
        to get an orientation near the end of half edge
        """
        mapped_point = point

        if lift == self.lifts[0]:
            mapped_point = self.segments[0].inverse_lift(mapped_point)
            mapped_point = self.segments[1].lift(mapped_point)

        elif lift == self.lifts[1]:
            mapped_point = self.segments[1].inverse_lift(mapped_point)
            mapped_point = self.segments[0].lift(mapped_point)

        else:
            print("error recognizing lift")

        return mapped_point

    def set_index(self, lift, index):
        """
        the index is the ordering of lifts along universal geodesic
        """
        if lift == self.lifts[0]:
            self.index = (index, self.index[1])

        elif lift == self.lifts[1]:
            self.index = (self.index[0], index)

        else:
            print("error setting index")

    def get_conjugate_index(self, lift):
        if lift == self.lifts[0]:
            return self.index[1]

        elif lift == self.lifts[1]:
            return self.index[0]

        else:
            print("error getting lift index")


class HalfEdge:
    def __init__(self, label):
        self.label = label
        self.nxt = None
        self.flip = None
        self.region = None

    def set_next(self, half_edge):
        self.nxt = half_edge

    def set_flip(self, half_edge):
        self.flip = half_edge

    def belongs_to(self, region):
        self.region = region


class Link:
    def __init__(self, zero_cell=None):
        """
        links are the graphs at zero-cells:
        we assume no triple intersections
        """
        self.zero_cell = zero_cell
        self.link_map = {(-1, 0): [], (0, 1): [], (1, 0): [], (0, -1): []}

    def euler(self):
        num_vertices = 0
        num_edges = 0

        for edges in self.link_map.values():
            if len(edges) > 1:
                num_vertices += 1
                num_edges += len(edges)

        num_edges = num_edges / 2

        return num_vertices - num_edges

    def full_link(self, label, removed_region):
        """
        keys are vertices values are list of edges at vertex
        """
        zero_cell = self.zero_cell
        vertices = list(self.link_map.keys())
        initial_half_edge = zero_cell.half_edges[0]
        current_half_edge = initial_half_edge.nxt.flip
        current_half_edge.zero_cell_label = zero_cell.label
        count = 0
        remove_labels = removed_region.get_labels()

        # create edges in attaching disc
        edge = ((-1, 0), (1, 0), "{}disc1".format(label))
        self.link_map[(-1, 0)].append(edge)
        self.link_map[(1, 0)].append(edge)

        edge = ((0, -1), (0, 1), "{}disc2".format(label))
        self.link_map[(0, -1)].append(edge)
        self.link_map[(0, 1)].append(edge)

        while initial_half_edge.label != current_half_edge.label:
            vertex1 = vertices[count]
            vertex2 = vertices[(count + 1) % 4]

            if current_half_edge.label not in remove_labels:
                edge = (vertex1, vertex2, current_half_edge.label)
                self.link_map[vertex1].append(edge)
                self.link_map[vertex2].append(edge)

            current_half_edge = current_half_edge.nxt.flip
            current_half_edge.zero_cell_label = zero_cell.label
            count += 1

        # get last edge
        vertex1 = vertices[count % 4]
        vertex2 = vertices[(count + 1) % 4]

        if current_half_edge.label not in remove_labels:
            edge = (vertex1, vertex2, current_half_edge.label)

        self.link_map[vertex1].append(edge)
        self.link_map[vertex2].append(edge)

    # returns tuple of sorted labels
    def get_labels(self):
        labels = []

        for edges in self.link_map.values():
            labels.extend([str(x[2]) for x in edges if str(x[2]) not in labels])

        for index in range(6 - len(labels)):
            labels.append("none")

        return tuple(labels)

    def set_edges(self, vertex, edges):
        self.link_map[vertex] = edges

    def remove_edge(self, edge):
        sub_link = Link()

        for vertex, edges in self.link_map.items():
            sub_link.set_edges(vertex, [x for x in edges if x != edge])

        return sub_link

    # remove edge if it is the only edge at a vertex
    def remove_stems(self):
        for vertex in self.link_map.keys():
            if len(self.link_map[vertex]) == 1:

                edge = self.link_map[vertex][0]
                new_link = self.remove_edge(edge)

                return new_link.remove_stems()

        return self

    def is_empty(self):
        number_of_edges = 0

        for vertex, edges in self.link_map.items():
            number_of_edges += len(edges)

        return True if number_of_edges < 5 else False

    # used for debuggin
    def number_of_edges(self):
        number_of_edges = 0

        for vertex, edges in self.link_map.items():
            number_of_edges += len(edges)

        return number_of_edges

    def get_equations(self):
        """
        find all sub graphs of valence at least 2
        """
        equations = []
        removed_edges = []

        for edges in self.link_map.values():
            for edge in edges:
                if edge in removed_edges:
                    pass
                else:
                    removed_edges.append(edge)

                    regular_section = self.remove_edge(edge)
                    regular_section = regular_section.remove_stems()

                    if regular_section.is_empty():
                        pass

                    else:
                        sub_equations = regular_section.get_equations()
                        equations.extend(
                            [
                                equation
                                for equation in sub_equations
                                if equation not in equations
                            ]
                        )

        if not self.is_empty():
            equations.append(
                {"labels": self.get_labels(), "constant": 2 - self.euler()}
            )

        return equations


class Region:
    def __init__(self, label):
        """a region is a two cell that lies in the fundamental domain"""
        self.label = label
        self.half_edges = []

    def add_half_edge(self, half_edge):
        self.half_edges.append(half_edge)

    def __len__(self):
        return len(self.half_edges)

    def print_region(self):
        for half_edge in self.half_edges:
            print(half_edge.label, "***")

    def get_equation(self):
        return [x.label for x in self.half_edges]

    def get_labels(self):
        """ returns labels of half edges in region"""
        return [half_edge.label for half_edge in self.half_edges]

    def get_vertices(self):
        return [x.zero_cell_label for x in self.half_edges]


class CellComplex:
    def __init__(self, half_edges):
        self.half_edges = half_edges
        self.regions = []
        label = 0

        for half_edge in half_edges:
            if half_edge.region is None:
                region = Region(label)
                region.add_half_edge(half_edge)
                half_edge.belongs_to(region)
                initial_label = half_edge.label
                next_half_edge = half_edge.nxt

                while next_half_edge.label != initial_label:
                    # print(next_half_edge.label, initial_label)
                    region.add_half_edge(next_half_edge)
                    next_half_edge.belongs_to(region)
                    next_half_edge = next_half_edge.nxt

                self.regions.append(region)
                label += 1

    def print_cell_complex(self):
        for region in self.regions:
            region.print_region()
