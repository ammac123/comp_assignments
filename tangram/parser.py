
from pathlib import Path
import sys
import re
import numpy as np

sys.path.append((Path.cwd() / 'tangram').__str__())

from elements.tangram import Tangram, TangramType
from fileHandler import FileHandler
from utils.coords import Number

test = Path.cwd() / 'tests' / 'cat.tex'


class LatexTangramParser:
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        self.tangrams = []

    def parse(self) -> list[Tangram]:
        for line_number, line in enumerate(self.lines, 1):
            tangram = self._parse_line(line)
            if tangram is not None:
                self.tangrams.append(tangram)
        return self.tangrams


    def _parse_line(self, line: str) -> Tangram | None:
        """Parse a single line to determine if there is a Tangram present"""
        # Regex to find a tangram and coords (based on TangramTikz package)
        pattern = re.compile(
                r'\[TangSol.*'
                r'(?P<params>(?<=\]<).*(?=>)|(?:(?=\]\()))'
                    r'.*'
                r'(?P<coords>'
                    r'(?P<x>(?<=({)).*)(?=(},))'
                        r'.*'
                    r'(?P<y>(?<=(,{)).*)(?=(}\))))'
                r'.*(?P<type>Tang(?:GrandTri|MoyTri|PetTri|Car|Para))'
            )
        # Pattern to match the params because I cannot for the life of me 
        # find a fucking pattern that works for both at once
        pattern_params = re.compile(
            r'((?P<params>(?<=<)[^>]*(?=>))*)'
        )
        line = re.sub(r'\s','',line)
        matches = pattern.search(line)

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
    pattern = re.compile(
        r'(?P<a_sign>[+-]?)'
            r'(?P<a>\d+(?:\.\d+)?|\.\d+)?'
        r'(?P<b_part>'
            r'(?P<b_sign>[+-]*)'
            r'(?:(?P<b>\d+(?:\.\d+)?|\.\d+)\*)?'
            r'sqrt\(2\)'
        r')?$')

    @staticmethod
    def parse(expression: str) -> tuple[float, float]:
        a_re = (
            r'(?P<a_part>^('    # Groups all 'a' matches into group
                r'(?P<a_sign>[+-]?)'    # Determines sign of 'a'
                r'(?P<a>(\d+|\d+\.\d+|\.\d+))'  # 'a' value
            r')(?=[+-]|$))' # Anchoring 'a' to either "+","-" or end of string
            r'?'    # Flag to match 0 or 1 times
        )
        b_re = (
            r'(?P<b_part>'  # Groups all 'b' matches into group
                r'(?P<b_sign>[+-]?)'    # Determines sign of 'b'
                r'(?P<b>(\d+|\d+\.\d+|\.\d+)?)' # 'b' value
            r'\*?sqrt\(2\)$)'   # Anchors 'b' to either "sqrt(2)" or "*sqrt(2)"
            r'?'    # Flag to match 0 or 1 times
        )
        pattern = re.compile(a_re + b_re)

        # Clean expression of whitespaces
        expression = re.sub(r'\s','',expression)

        match = pattern.match(expression)

        if not match:
            return None
        
        # Parsing a
        rational = 0.0
        if match.group('a_part'):
            a_value = match.group('a')
            a_sign = match.group('a_sign')
            a_value = float(a_value)
            if a_sign == '-':
                a_value = -a_value
            rational = a_value

        # Parsing b
        irrational = 0.0
        if match.group('b_part'):
            b_value = match.group('b')
            b_sign = match.group('b_sign')
            if b_value:
                b_value = float(b_value)
            else:
                b_value = 1.0
            if b_sign == '-':
                b_value = -b_value

            irrational = b_value
            

        return (rational, irrational)