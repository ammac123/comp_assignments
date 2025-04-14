
from pathlib import Path
import sys
import re
import numpy as np

sys.path.append((Path.cwd() / 'tangram').__str__())

from elements.tangram import Tangram, TangramType
from fileHandler import FileHandler
from utils.coords import Number

test = Path.cwd() / 'tests' / 'cat.tex'

raw = FileHandler.read_file(test)
class LatexTangramParser:
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        self.tangrams = []

    def parse(self) -> list[Tangram]:
        for line_number, line in enumerate(self.lines, 1):
            pass

    def _parse_line(self, line: str, line_number: int) -> Tangram | None:
        """Parse a single line to determine if there is a Tangram present"""
        # Regex to find a tangram (based on TangramTikz package)
        pattern = re.compile(r'<(?P<params>[^>]*)\>\(\{(?P<x>[^}]+)\},\{(?P<y>[^}]+)\}\)\{(?P<type>Tang(?:GrandTri|MoyTri|PetTri|Car|Para))\}')
        
        matches = re.search(pattern=pattern, string=line)

        if matches is None:
            return None
        
        # Parse type
        type_map = {
            'TangGrandTri': TangramType.TRIANGLE_LARGE,
            'TangMoyTri': TangramType.TRIANGLE_MEDIUM,
            'TangPetTri': TangramType.TRIANGLE_SMALL,
            'TangCar': TangramType.SQUARE,
            'TangPara': TangramType.PARALLELOGRAM
        }

        tangram_type = type_map[matches.group('type')]

        # Parse transform parameters
        transform_params = {}
        if matches.group('params'):
            params = matches.group('params').split(',')
            for param in params:
                key, value = param.split('=')
                transform_params[key.strip()] = int(value.strip())

        # Parse coordinates
        x_rat, x_irrat = CoordParser.parse(matches.group('x'))
        x_coord = Number(x_rat, x_irrat)
        y_rat, y_irrat = CoordParser.parse(matches.group('y'))
        y_coord = Number(y_rat, y_irrat)

        return Tangram(tangram_type=tangram_type, transform_params=transform_params, base_coords=(x_coord, y_coord))



class CoordParser:
    pattern = r'^(?P<a_value>[+-]?(?:\d*\.?\d+)?)?(?:(?P<operator>[+-])?(?:(?P<b_value>\d*\.?\d+)?\*?)?sqrt\(2\))?$'

    @staticmethod
    def parse(expression: str) -> tuple[float, float]:

        pattern = re.compile(CoordParser.pattern, re.VERBOSE)
        match = pattern.match(expression.strip())

        if not match:
            raise ValueError(f'Invalid coordinates {expression}')
        
        a_value = match.group('a_value') or '0'
        b_value = match.group('b_value') or '1'
        operator = match.group('operator') or '0'

        rational = float(a_value) if a_value else 0.0

        if 'sqrt(2)' not in expression:
            return (rational, 0.0)
        
        irrational = float(b_value)
        if operator == '-':
            irrational = -irrational

        return (rational, irrational)
    


test = '\\PieceTangram[TangSol]<xscale=-1,rotate=3735>({-000.500},{-0.5-sqrt(2)}){TangPetTri}'

pat = re.compile(r"(?:\<(?P<params>[^\]]*)\>)?(?P<full>\(\{(?P<x>[^}]+)\},\s*\{(?P<y>[^}]+)\}\))(?P<type>Tang(?:GrandTri|MoyTri|PetTri|Car|Para))")

pat1 = r'<(?P<params>[^>]*)\>\(\{(?P<x>[^}]+)\},\{(?P<y>[^}]+)\}\)\{(?P<type>Tang(?:GrandTri|MoyTri|PetTri|Car|Para))\}'

matches = re.search(pattern=pat1, string=test)

matches.group('x')
matches.group('y')
matches.group('type')

dict(param.split('=') for param in matches.group('params').split(","))



l = LatexTangramParser(test)

m = l._parse_line(line=test, line_number=0)


m.vertices
