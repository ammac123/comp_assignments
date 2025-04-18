
from pathlib import Path
import sys
from collections import deque

sys.path.append((Path.cwd() / 'tangram').__str__())
from elements.base import LatexElement
from enum import Enum, auto
from typing import Literal
from utils.coords import arc_sort, Number

_TEX_OBJECTS = Literal['outline', 'pieces']


class TangramType(Enum):
    TRIANGLE_LARGE = auto()
    TRIANGLE_MEDIUM = auto()
    TRIANGLE_SMALL = auto()
    SQUARE = auto()
    PARALLELOGRAM = auto()

    def __repr__(self):
        return super().__repr__()
    
    def __str__(self):
        _smap = {
        TangramType.TRIANGLE_LARGE: 'Large triangle',
        TangramType.TRIANGLE_MEDIUM: 'Medium triangle',
        TangramType.TRIANGLE_SMALL: 'Small triangle',
        TangramType.SQUARE: 'Square',
        TangramType.PARALLELOGRAM: 'Parallelogram',
    }
        return f"{_smap[self]}"


rotation_values = {
            0: (Number(1, 0), Number(0, 0)),
            45: (Number(0, 1/2), Number(0, 1/2)),
            90: (Number(0, 0), Number(1, 0)),
            135: (Number(0, -1/2), Number(0, 1/2)),
            180: (Number(-1, 0), Number(0, 0)),
            225: (Number(0, -1/2), Number(0, -1/2)),
            270: (Number(0, 0), Number(-1, 0)),
            315: (Number(0, 1/2), Number(0, -1/2))
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

class Tangram(LatexElement):

    def __init__(self, tangram_type: TangramType, transform_params={}, base_coords=(0,0), line_number=None, content=None):
        super().__init__(content, line_number)
        if isinstance(tangram_type, int):
            self.tangram_type = TangramType(tangram_type)
        else:
            self.tangram_type = tangram_type
        self.transforms(transform_params)
        self.base_coords = base_coords
        self.vertices = self._find_verticies()
        self.transformations = {
            'xflip': self.xflip,
            'yflip': self.yflip,
            'rotate': self.rotate,
        }

    @property
    def _grid(self):
        min_x = min(self.vertices, key=lambda x: x[0])[0]
        min_y = min(self.vertices, key=lambda x: x[1])[1]

        max_x = max(self.vertices, key=lambda x: x[0])[0]
        max_y = max(self.vertices, key=lambda x: x[1])[1]
        return ((min_x, min_y), (max_x, max_y))

    def transforms(self, transform_params: dict):
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
        
        self.xflip = xflip
        self.yflip = yflip
        self.rotate = rotate
        return
    

    def _find_verticies(self):
        """
        Find all vertices of the tangram piece after transformations.
        These vertices are sorted from leftmost topmost.

        Returns list of (x,y) coordinate tuples. 
        """
        vertices = base_shapes[self.tangram_type]

        # Apply transformations based on tangram params
        if self.rotate:
            cos_theta, sin_theta = rotation_values[self.rotate]
            rotated_vertices = []
            for x, y in vertices:
                # Rotation matrix multiplication with Number objects
                new_x = x * cos_theta - y * sin_theta
                new_y = x * sin_theta + y * cos_theta
                rotated_vertices.append((new_x, new_y))
            vertices = rotated_vertices
        
        if self.xflip:
            vertices = [(-x, y) for x, y in vertices]
        
        if self.yflip:
            vertices = [(x, -y) for x, y in vertices]

        # Shift vertices by base coordinates
        vertices = [(x + self.base_coords[0], y + self.base_coords[1]) 
               for x, y in vertices]
        
        topleft_vertex = max(vertices, key=lambda v: (v[1],-v[0]))
        
        start_idx = vertices.index(topleft_vertex)
        # start_idx = 0
        # for idx, v in enumerate(vertices):
        #     if v[1] == vertices[start_idx][1] and v[0] < vertices[start_idx][0]:
        #         start_idx = idx
            
        #     elif v[1] > vertices[start_idx][1]:
        #         start_idx = idx
                

        # Rotating clockwise to find next point
        start_vertex = vertices[start_idx]
        angles = []
        for vertex in vertices:
            angles.append(-arc_sort(start_vertex, vertex))

        vertices_sorted = deque([v for _, v in sorted(zip(angles, vertices), reverse=True)])
        
        # Ensuring the start point is the starting point
        start_idx = vertices_sorted.index(start_vertex)
        vertices_sorted.rotate(-start_idx)

        return list(vertices_sorted)

    
    def __repr__(self):
        return f"Tangram (Type: {self.tangram_type}, Transforms: {{xflip: {self.xflip}, yflip: {self.xflip}, rotate: {self.rotate}}}, Base: {self.base_coords})"
    
    def __str__(self):
        return f"Tangram (Type: {self.tangram_type}, Transforms: {{xflip: {self.xflip}, yflip: {self.xflip}, rotate: {self.rotate}}}, Base: {self.base_coords})"



class TexTangram(LatexElement):
    def __init__(self, tangram:Tangram, type:_TEX_OBJECTS):
        self.vertices = tangram.vertices
        super().__init__(content=None, line_number=None)
        if type == 'pieces':
            self.content = self._generate_piece()

    @staticmethod
    def _generate_coordinate(x:Number|int, y:Number|int):
        if isinstance(x, Number):
            x = x.coordinate_format()
        if isinstance(y, Number):
            y = y.coordinate_format()
        
        x_str = r'{'+str(x)+r'}'
        y_str = r'{'+str(y)+r'}' 

        return f'({x_str}, {y_str})'
        

    def _generate_piece(self) -> str:
        string_list = []
        for x,y in self.vertices:
            string_list.append(self._generate_coordinate(x,y))
        string_list.append('cycle;')
        content = r'\draw[ultra thick] ' + ' -- '.join(string_list)
        return content