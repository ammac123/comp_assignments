import math
from collections import defaultdict, Counter
from shapely.geometry import Polygon
from shapely.ops import unary_union

def outer_boundary(tangrams):
    polygons = [Polygon(t) for t in tangrams]

    merged = unary_union(polygons)

    outer_boundary = list(merged.exterior.coords)

    return outer_boundary


def get_edges(polygon):
    n = len(polygon)
    return [(polygon[i], polygon[(i+1) % n]) for i in range(n)]

def canonical_edge(a, b):
    return tuple(sorted([a, b]))

def find_boundary(polygons):
    edge_counter = Counter()
    directed_edges = []

    # Step 1 & 2: Count canonical edges
    for poly in polygons:
        for a, b in get_edges(poly):
            ce = canonical_edge(a, b)
            edge_counter[ce] += 1
            directed_edges.append((a, b))

    # Step 3: Keep edges that appear only once (boundary)
    boundary_edges = [edge for edge in directed_edges if edge_counter[canonical_edge(*edge)] == 1]

    # Step 4: Reconstruct the boundary path
    # Build adjacency list
    adjacency = defaultdict(list)
    for a, b in boundary_edges:
        adjacency[a].append(b)

    # Trace the boundary path(s)
    boundaries = []
    visited = set()

    def trace_path(start):
        path = [start]
        current = start
        while True:
            neighbors = [n for n in adjacency[current] if (current, n) not in visited]
            if not neighbors:
                break
            next_point = neighbors[0]
            visited.add((current, next_point))
            path.append(next_point)
            current = next_point
        return path

    # Could be multiple boundary loops
    for a, b in boundary_edges:
        if (a, b) not in visited:
            visited.add((a, b))
            path = trace_path(b)
            boundaries.append([a] + path)

    return boundaries



def point_on_segment(p, a, b, tol=1e-8):
    """Check if point p lies on segment ab."""
    ax, ay = a
    bx, by = b
    px, py = p
    cross = (bx - ax)*(py - ay) - (by - ay)*(px - ax)
    if abs(cross) > tol:
        return False
    dot = (px - ax)*(bx - ax) + (py - ay)*(by - ay)
    if dot < 0:
        return False
    squared_len = (bx - ax)**2 + (by - ay)**2
    return dot <= squared_len

def split_edges(boundaries):
    edges = []
    for boundary in boundaries:
        n = len(boundary)
        for i in range(n):
            a = boundary[i]
            b = boundary[(i + 1) % n]
            edges.append((a, b))

    # Collect all points
    points = set(p for edge in edges for p in edge)

    # New edges after splitting
    split_edges = []

    for a, b in edges:
        # Find intermediate points on segment (a, b)
        on_seg = [p for p in points if p != a and p != b and point_on_segment(p, a, b)]
        if not on_seg:
            split_edges.append((a, b))
        else:
            # Sort points along segment
            def dist(p1, p2):
                return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2
            all_points = [a] + sorted(on_seg, key=lambda p: dist(a, p)) + [b]
            for i in range(len(all_points) - 1):
                split_edges.append((all_points[i], all_points[i+1]))

    return split_edges


def build_graph(edges):
    graph = defaultdict(set)
    for a, b in edges:
        graph[a].add(b)
        graph[b].add(a)
    return graph

def angle_from(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def trace_outer_boundary(graph):
    # Start from the leftmost (and bottom-most) point
    start = min(graph.keys(), key=lambda p: (p[0], p[1]))
    path = [start]
    current = start
    prev_angle = -math.pi  # start going leftward

    while True:
        neighbors = list(graph[current])
        if not neighbors:
            break
        # Choose the next point that makes the smallest left turn
        neighbors.sort(key=lambda p: (angle_from(current, p) - prev_angle) % (2 * math.pi))
        next_point = neighbors[0]
        graph[current].remove(next_point)
        graph[next_point].remove(current)
        if next_point == start:
            path.append(start)
            break
        path.append(next_point)
        prev_angle = angle_from(current, next_point)
        current = next_point

    return path
