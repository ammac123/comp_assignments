
from collections import defaultdict
from functools import total_ordering
from fractions import Fraction
import numpy as np

def arc_sort(x: tuple[float], y: tuple[float], offset: float = 0.0):
    dx = y[0] - x[0]
    dy = y[1] - x[1]
    theta = np.arctan2(float(dx), float(dy))
    return (theta + offset)%(2*np.pi)

@total_ordering
class Number:
    def __init__(self, rational: float = 0, irrational: float = 0):
        """
        Create a number in the form: rational + irrational*√2
        
        Args:
            rational (float): The rational part of the number
            irrational (float): The coefficient of √2
        """
        self.rational = float(rational)
        self.irrational = float(irrational)

    def coordinate_format(self) -> str:
        coordinate = self.__repr__()
        coordinate = coordinate.replace('(','').replace(')','').replace(' ','')
        if abs(self.irrational) == 1:
            coordinate = coordinate.replace('√2','sqrt(2)')
        else:
            coordinate = coordinate.replace('√2','*sqrt(2)')
        return coordinate

    def _format_number(self, num: float) -> str:
        """Format a number as integer or fraction."""
        fraction = Fraction(num).limit_denominator()
        if fraction.denominator == 1:
            return str(fraction.numerator)
        return f"{fraction.numerator}/{fraction.denominator}"

    def __eq__(self, other):
        if isinstance(other, Number):
            if self.rational == other.rational and self.irrational == other.irrational:
                return True
            else:
                self.__float__() == other.__float__()
        return self.__float__() == other.__float__()

    def __lt__(self, other):
        return self.__float__() < other.__float__()
    
    def __neg__(self):
        """Handle negation (-x)"""
        return Number(-self.rational, -self.irrational)
    
    def __pos__(self):
        """Handle unary plus (+x)"""
        return self
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Number(self.rational + other, self.irrational)
        return Number(self.rational + other.rational, self.irrational + other.irrational)
    
    def __radd__(self, other):
        """Handle right addition (other + self)"""
        return self.__add__(other)
    
    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Number(self.rational - other, self.irrational)
        return Number(self.rational - other.rational, self.irrational - other.irrational)
    
    def __rsub__(self, other):
        """Handle right subtraction (other - self)"""
        return Number(other, 0) - self
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Number(self.rational * other, self.irrational * other)
        # (a + b√2)(c + d√2) = (ac + 2bd) + (ad + bc)√2
        return Number(
            self.rational * other.rational + 2 * self.irrational * other.irrational,
            self.rational * other.irrational + self.irrational * other.rational
        )
    
    def __rmul__(self, other):
        """Handle right multiplication (other * self)"""
        return self.__mul__(other)
    
    def __float__(self):
        """Convert to floating point number"""
        return float(self.rational) + float(self.irrational * pow(2,0.5))
    
    def __mod__(self, other):
        """Handles the modulus operator"""
        if isinstance(other, (int, float)):
            return self.__float__() % other
        
    def __hash__(self):
        return hash(self.__float__())
    
    def __abs__(self):
        return abs(self.__float__())
    
    def __pow__(self, other):
        if isinstance(other, (int, float)):
            return pow(self.__float__(), other)
    
    
    def __repr__(self):
        parts = []
        
        # Add rational part if non-zero
        if self.rational != 0:
            parts.append(self._format_number(self.rational))
        
        # Handle irrational part
        if self.irrational != 0:
            # Format the coefficient
            if abs(self.irrational) == 1:
                # Just show √2 with appropriate sign
                if self.rational != 0:
                    parts.append(" + " if self.irrational > 0 else " - ")
                    parts.append("√2")
                else:
                    parts.append("" if self.irrational > 0 else "-")
                    parts.append("√2")
            else:
                # Show coefficient with √2
                if parts and self.irrational > 0:
                    parts.append(" + ")
                elif self.rational != 0 and parts and self.irrational < 0:
                    parts.append(" - ")

                if self.rational != 0 and self.irrational % 1 == 0:
                    coeff = self._format_number(abs(self.irrational))
                    parts.append(f"{coeff}√2")

                elif self.rational == 0 and self.irrational % 1 == 0:
                    coeff = self._format_number(abs(self.irrational))
                    parts.append(f"{coeff}√2")

                elif self.rational != 0:
                    coeff = self._format_number(abs(self.irrational))
                    parts.append(f"({coeff})√2")

                else:
                    coeff = self._format_number(self.irrational)
                    parts.append(f"({coeff})√2")
        
        # Return "0" if both parts are zero
        if not parts:
            return "0"
        
        return "".join(parts)
    

def canonical_edge(a, b):
    """Sort edge vertices so direction doesnt matter"""
    return tuple(sorted([a, b]))

def find_boundary_edges(polygons):
    edge_count = defaultdict(int)

    for poly in polygons:
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            edge = canonical_edge(a, b)
            edge_count[edge] += 1

    # Boundary edges appear only once
    boundary_edges = [edge for edge, count in edge_count.items() if count == 1]
    return boundary_edges

