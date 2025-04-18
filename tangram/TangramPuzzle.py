
from pathlib import Path
import sys
import re
from typing import Literal
import numpy as np

_BOUNDS = Literal['upper','lower']

sys.path.append((Path.cwd() / 'tangram').__str__())

from elements.tangram import Tangram, TangramType
from elements.document import TangramPieces
from fileHandler import FileHandler
from parser import LatexTangramParser, CoordParser
from utils.coords import Number, arc_sort, find_boundary_edges
from utils.boundary import find_boundary, point_on_segment, outer_boundary
from collections import Counter, defaultdict
from shapely import geometry
from shapely.ops import unary_union


class TangramPuzzle:
    
    def __init__(self, file: str):
        raw = FileHandler.read_file(filename=file)
        self.tangrams = LatexTangramParser(raw_text=raw).parse()
        self.transformations = self._transforms()
        self.sorted_tangrams = self._sort()

    @property
    def grid_size(self) -> list[tuple]:
        def add_boundary_space(coord: float, sign:_BOUNDS):
            coord = float(coord)
            bound = 0.0
            if sign == 'lower':
                coord = -coord
            if coord % 0.5 == 0:
                bound = coord + 0.5
            else:
                bound = coord - (coord % 0.5) + 1
            
            if sign == 'lower':
                bound = -bound
            return bound
        
        grids = [gram._grid for gram in self.tangrams]

        # Adding space to the boundary of the grid, 
        # at least one grid space but no more than two
        min_x = add_boundary_space(min(grids, key=lambda g: g[0][0])[0][0], 'lower')
        min_y = add_boundary_space(min(grids, key=lambda g: g[0][1])[0][1], 'lower')
        max_x = add_boundary_space(max(grids, key=lambda g: g[1][0])[1][0], 'upper')
        max_y = add_boundary_space(max(grids, key=lambda g: g[1][1])[1][1], 'upper')

        return ((min_x, min_y), (max_x, max_y))
    
    def _puzzle_verticies(self):
        verticies = []
        verticies.extend((t.vertices for t in self.tangrams))
        
        return verticies
    
    def _sort(self) -> list[Tangram]:
        def sort_key(t: Tangram):
            key = []
            first_vertex = t.vertices[0]
            key.append(float(-first_vertex[1]))
            key.append(float(first_vertex[0]))
            for vertex in t.vertices[::-1]:
                key.append(float(vertex[0]))
            return tuple(key)
        
        sorted_grams = sorted(self.tangrams, key=sort_key)
        
        return sorted_grams

    def _transforms(self) -> dict:
        count_pieces = Counter([x.tangram_type for x in self.tangrams])
        transform_dict = {}
        for gram in self.tangrams:
            if count_pieces[gram.tangram_type] == 1:
                key = f'{gram.tangram_type}'
            else:
                count = 1
                while True:
                    key = f'{gram.tangram_type} {count}'
                    if key not in transform_dict.keys():
                        break
                    count += 1

            transform_dict[key] = gram.transformations

        return transform_dict

    def draw_pieces(self, filename, writeout:bool=True):
        pieces_content = TangramPieces(self.grid_size, self.sorted_tangrams).generate_content()
        if writeout:
            FileHandler.write_tex(content=pieces_content, filename=filename)
        else:
            return pieces_content


    def __str__(self):
        str_out = []
        sorted_tangrams = self.sorted_tangrams
        for gram in sorted_tangrams:
            str_out.append(f'{gram.tangram_type:15}: {gram.vertices}')
        return '\n'.join(str_out)