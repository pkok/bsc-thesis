from itertools import product

class Quadtree(object):

    """A dimension-free implementation of quadtrees and octrees.

    This class provides a general implementation of quadtrees for any
    dimensionality.  Quadtrees are datastructures for storing 2D 
    points (represented by a tuple), which can be associated with a 
    value.  Their 3D counterparts are called octrees.

    Each node can contain points within a certain area or
    (hyper-)volume.  The ranges of this body are given as a list of
    2-tuples.  The first member of the tuple is an inclusive lower
    bound; the second an exclusive upper bound.
    
    Each node has a threshold on the number of points it can contain.
    If the threshold is exceeded, it will split and divide the contained
    points among its new children.

    A maximum depth of the tree can be given.  If there is no upper
    bound on the tree depth, max_depth should be negative.

    Some examples of instantiating a Quadtree:

    Quadtree([(x1, x2), (y1, y2)]) -> an empty quadtree, which can
        contain points (px, py) for which x1 <= px < x2, y1 <= py < y2.
        Each node can contain up to 1 point before splitting.

    Quadtree([(x1, x2), (y1, y2), (z1, z2)]) -> an empty octree which
        can contain points (px, py, pz) for which x1 <= px < x2,
        y1 <= py < y2, z1 <= pz < z2.  Each node can contain up to 1
        point before splitting.

    Quadtree(ranges, threshold=5) -> an empty Quadtree.  Each node can
        contain up to 5 points before splitting.

    Quadtree(ranges, max_depth=8) -> an empty Quadtree with a maximum
        depth of 8.

    """
    
    def __init__(self, ranges, threshold=1, max_depth=-1, parent=None):
        """Initializes a Quadtree."""

        self.ranges = []
        for range in ranges:
            if range[0] > range[1]:
                self.ranges.append((range[1], range[0]))
            else:
                self.ranges.append((range[0], range[1]))
        self.threshold = threshold
        self.max_depth = max_depth
        self.parent = parent
        self.points = {}
        self._is_full = False
        self.children = None

    def __len__(self):
        """Number of points contained in self and its children."""
        if self.children:
            return sum((len(child) for child in self.children))
        return len(self.points)

    def __repr__(self):
        """A technical string representation."""
        return "<%s.%s range: %s; size: %s>" % (self.__module__,
                self.__class__.__name__, self.ranges, len(self))

    def __contains__(self, point):
        """Check if a point is contained by the tree."""
        nearest_neighbour = self.nearest_neighbour(point)
        if nearest_neighbour is None:
            return False
        return (nearest_neighbour[0] == point)

    def __delitem__(self, point):
        """Delete a point.
        
        del x[point] behaves exactly the same as x.delete(point).
        
        """
        return self.delete(point)

    def __getitem__(self, point):
        """Retrieve a point's value from the collection."""
        nearest_neighbour = self.nearest_neighbour(point)
        if nearest_neighbour is None or nearest_neighbour[0] != point:
            # raise something
            raise KeyError(point)
        return nearest_neighbour[1]

    def __setitem__(self, point, value):
        """Add a point with a certain value to the tree.
        
        x[point] = value behave exactly the same as x.add(point, value)
        
        """
        return self.add(point, value)

    def __iter__(self):
        """Return an iterator over all contained points."""
        class NodeIterator(object):
            def __init__(self, node):
                self.node_stack = [node]
                self.point_stack = []

            def __iter__(self):
                return self

            def next(self):
                while not self.point_stack:
                    if not self.node_stack:
                        raise StopIteration
                    node = self.node_stack.pop()
                    if node.children:
                        self.node_stack.extend(node.children)
                    else:
                        self.point_stack.extend(node.points.iteritems())

                p = self.point_stack.pop()
                return p

        return NodeIterator(self)

    def _fetch_containing_node(self, point, value=None):
        """Return the node containing the point."""
        point_on_line = lambda d: d[0][0] <= d[1] < d[0][1]
        point_in_space = \
                lambda n, p: all(map(point_on_line, zip(n.ranges, p)))

        if not self._is_full:
            if point_in_space(self, point):
                return self
        else:
            for node in self.children:
                if point_in_space(node, point):
                    return node._fetch_containing_node(point, value)
        return None

    def _collides_with_sphere(self, center, radius):
        """Test if a sphere collides or touches the node's cube.

        This is an implementation of the algorithm described in "A 
        simple method for box-sphere intersection testing" by James 
        Arvo.

        """
        d_min = 0
        B_mins, B_maxs = zip(*self.ranges)
        for B_min, B_max, C in zip(B_mins, B_maxs, center):
            if C < B_min:
                d_min += (C - B_min) * (C - B_min)
            elif C > B_max:
                d_min += (C - B_max) * (C - B_max)
        return d_min <= (radius * radius)

    def _split(self):
        """Create self's children and divide self's points among them.

        This is a helper routine of the add mechanism.

        """
        self.children = []
        self._is_full = True
        new_ranges = []
        for ranges in self.ranges:
            middle = ranges[0] + ((ranges[1] - ranges[0]) / 2)
            new_ranges.append([(ranges[0], middle), (middle, ranges[1])])
        new_ranges = product(*new_ranges)
        for ranges in new_ranges:
            self.children.append(self.__class__(ranges, self.threshold, 
                                                self.max_depth - 1,
                                                self))
        for point in self.points:
            self.add(point, self.points[point])
        self.points = None

    def add(self, point, value=None):
        """Add a point to the collection."""
        # Check if the point is in the area!
        for range, p in zip(self.ranges, point):
            if not range[0] <= p < range[1]:
                raise KeyError(point)
        # If this node is full, find the child node that contains point.
        if self._is_full:
            node = self._fetch_containing_node(point, value)
            if node is None or node is self:
                raise LookupError("point is not in the node's area.")
            node.add(point, value)
        # When the node is full and not at the maximum depth, split it.
        elif len(self.points) == self.threshold and self.max_depth:
            self._split()
            self.add(point, value)
        # But by default, add the point with its associated value in the node.
        else:
            self.points[point] = value

    def delete(self, point, value=None):
        """Remove a point from the collection.

        If value is not None, it checks if the associated value of the 
        point found is the same as value.  It does not delete redundant
        nodes.
        
        """
        if not self._is_full:
            if value is not None:
                if value == self.points[point]:
                    del self.points[point] 
            else:
                del self.points[point] 
        else:
            child = self._fetch_containing_node(point)
            child.delete(point, value)

    # FIXME plz?
    def k_nearest_neighbour(self, k, target):
        """Look for the set of k points which are closest to target.

        Currently only implemented for k = 1.  Other values for k raise
        a NotImplementedError.

        """
        if k == 1:
            return self.nearest_neighbour(target)
        raise NotImplementedError()

    def nearest_neighbour(self, target):
        """Find the point closest to target."""
        unvisited_nodes = [self]
        distance_vector = [abs(x[1] - x[0]) for x in self.ranges]
        search_radius = sum(x*x for x in distance_vector)
        nearest_neighbour = None
        while unvisited_nodes:
            node = unvisited_nodes.pop()
            if not node._is_full:
                # For each point p in node, check compute its distance and
                # check if it is closer than any other point you've seen.
                for p in node.points:
                    if p == target:
                        return p
                    difference_vector = map(lambda p1, p2: p1 - p2, target, p)
                    norm = sum(x*x for x in difference_vector)
                    if norm < search_radius:
                        nearest_neighbour = (p, node.points[p])
                        search_radius = norm
            else:
                for child in node.children:
                    if child._collides_with_sphere(target, search_radius):
                        unvisited_nodes.append(child)
        return nearest_neighbour
