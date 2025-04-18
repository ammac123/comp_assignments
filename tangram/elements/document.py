from pathlib import Path
import sys
from collections import deque

sys.path.append((Path.cwd() / 'tangram').__str__())
from elements.base import LatexElement
from elements.tangram import Tangram, TangramType, TexTangram
from enum import Enum, auto
from utils.coords import arc_sort, Number

document_header = [
        r'\documentclass{standalone}',
        r'\usepackage{tikz}',
        r'\begin{document}',
        '',
        r'\begin{tikzpicture}'
    ]
document_footer = [
    r'\end{tikzpicture}',
    '',
    r'\end{document}',
]
class TangramPieces:
    def __init__(self, grid: tuple[tuple], tangrams: list[Tangram]):
        self.origin = r'\fill[red] (0,0) circle (3pt);'
        self.grid = grid
        self.tangrams = tangrams
        pass

    @property
    def grid_definition(self):
        return r'\draw[step=5mm] ' + str(self.grid[0]) + ' grid ' + str(self.grid[1]) + ';'
    
    def _generate_tangram_body(self):
        content = ['\t'+self.grid_definition]
        for gram in self.tangrams:
            content.append('\t' + TexTangram(tangram=gram, type='pieces').content)
        content.append('\t' + self.origin)
        return '\n'.join(content)
    
    def generate_content(self):
        tangram_body = self._generate_tangram_body()
        content = '\n'.join(document_header) + '\n'
        content += tangram_body + '\n'
        content += '\n'.join(document_footer)
        self.content = content
        return content