
from pathlib import Path
import sys

sys.path.append((Path.cwd() / 'tangram').__str__())
from elements.base import LatexElement
from enum import Enum, auto
import numpy as np


class TangramType(Enum):
    TRIANGLE_LARGE = auto()
    TRIANGLE_MEDIUM = auto()
    TRIANGLE_SMALL = auto()
    SQUARE = auto()
    PARALLELOGRAM = auto()

    def __repr__(self):
        return super().__repr__()
    
    def __str__(self):
        return f"{self.name}"


class Tangram(LatexElement):
    def __init__(self, tangram_type: TangramType, transform_params={}, base_coords=(0,0), line_number=None, content=None):
        super().__init__(content, line_number)
        if isinstance(tangram_type, int):
            self.tangram_type = TangramType(tangram_type)
        else:
            self.tangram_type = tangram_type
        self.xflip, self.yflip, self.rotate = self.transforms(transform_params)
        self.base_coords = base_coords
        self.vertices = self._find_verticies()

    
    @staticmethod
    def transforms(transform_params: dict):
        xscale = transform_params.get('xscale', 0)
        yscale = transform_params.get('yscale', 0)
        rotate = transform_params.get('rotate', 0)
        
        # Ensure all values are ints
        if not isinstance(rotate, int):
            raise TypeError(f'expected "int" for rotate, got ({type(rotate).__name__}) instead.')
        
        if not isinstance(yscale, int):
            raise TypeError(f'expected "int" for yscale, got ({type(yscale).__name__}) instead.')
        
        if not isinstance(xscale, int):
            raise TypeError(f'expected "int" for xscale, got ({type(xscale).__name__}) instead.')

        # Handle cases for when object is flipped on both x- and y-axis
        if xscale == yscale == -1:
            rotate += 180
            xscale = 0
            yscale = 0

        # Normalise negative rotations
        rotate = rotate % 360

        # Determining flips
        xflip = xscale == -1
        yflip = yscale == -1
        
        return xflip, yflip, rotate
    

    def _find_verticies(self):
        """
        Find all vertices of the tangram piece after transformations.
        These vertices are sorted from leftmost topmost.

        Returns list of (x,y) coordinate tuples. 
        """
        from utils.coords import Number
        SQRT2 = Number(0, 1)
        rotation_values = {
            0: (Number(1, 0), Number(0, 0)),
            45: (Number(1/2, 1/2), Number(1/2, 1/2)),
            90: (Number(0, 0), Number(1, 0)),
            135: (Number(-1/2, -1/2), Number(1/2, 1/2)),
            180: (Number(-1, 0), Number(0, 0)),
            225: (Number(-1/2, -1/2), Number(-1/2, -1/2)),
            270: (Number(0, 0), Number(-1, 0)),
            315: (Number(1/2, 1/2), Number(-1/2, -1/2))
        }

        base_shapes = {
            TangramType.TRIANGLE_LARGE: [(Number(0),Number(0)), 
                                         (Number(2),Number(0)), 
                                         (Number(2),Number(2))],
            TangramType.TRIANGLE_MEDIUM: [(Number(0),Number(0)), 
                                         (Number(2),Number(0)), 
                                         (Number(1),Number(1))],
            TangramType.TRIANGLE_SMALL: [(Number(0),Number(0)),
                                         (Number(1),Number(0)), 
                                         (Number(1),Number(1))],
            TangramType.SQUARE: [(Number(0),Number(0)),
                                 (Number(1),Number(0)),
                                 (Number(1),Number(1)),
                                 (Number(0),Number(1))],
            TangramType.PARALLELOGRAM: [(Number(0),Number(0)),
                                        (Number(1),Number(0)),
                                        (Number(2),Number(1)),
                                        (Number(1),Number(1))],
        }

        vertices = base_shapes[self.tangram_type]

        # Apply transformations based on tangram params
        if self.xflip:
            vertices = [(-x, y) for x, y in vertices]
        
        if self.yflip:
            vertices = [(x, -y) for x, y in vertices]

        if self.rotate:
            cos_theta, sin_theta = rotation_values[self.rotate]
            rotated_vertices = []
            for x, y in vertices:
                # Rotation matrix multiplication with Number objects
                new_x = x * cos_theta - y * sin_theta
                new_y = x * sin_theta + y * cos_theta
                rotated_vertices.append((new_x, new_y))
            vertices = rotated_vertices

        # Shift vertices by base coordinates
        vertices = [(x + self.base_coords[0], y + self.base_coords[1]) 
               for x, y in vertices]

        start_idx = 0
        for idx, (x, y) in enumerate(vertices):
            current_vertex = vertices[start_idx]
            # Convert Number objects to float for comparison
            current_x = float(current_vertex[0])
            current_y = float(current_vertex[1])
            x_val = float(x)
            y_val = float(y)
            if x_val < current_x or (x_val == current_x and y_val > current_y):
                start_idx = idx

        # Rotating clockwise to find next point
        start_vertex = vertices[start_idx]
        angles = []
        for vertex in vertices:
            x_delta = float(vertex[0] - start_vertex[0])
            y_delta = float(vertex[1] - start_vertex[1])
            angle = np.arctan2(y_delta, x_delta)  # Note: swapped x_delta and y_delta for correct angle
            # Adjusting so clockwise starts from top
            angle = (angle + np.pi/2) % (2*np.pi)
            angles.append(angle)

        vertices_sorted = [v for _, v in sorted(zip(angles, vertices))]
        
        # Ensuring the start point is the starting point
        start_idx = vertices_sorted.index(start_vertex)
        vertices_sorted = vertices_sorted[start_idx:] + vertices_sorted[:start_idx]

        return vertices_sorted

    
    def __repr__(self):
        return f"Tangram (Type: {self.tangram_type}, Transforms: {{xflip: {self.xflip}, yflip: {self.xflip}, rotate: {self.rotate}}}, Base: {self.base_coords})"