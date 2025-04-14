
from functools import total_ordering
from fractions import Fraction

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

    def _format_number(self, num: float) -> str:
        """Format a number as integer or fraction."""
        fraction = Fraction(num).limit_denominator()
        if fraction.denominator == 1:
            return str(fraction.numerator)
        return f"{fraction.numerator}/{fraction.denominator}"
    
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
        return self.rational + self.irrational * (2 ** 0.5)
    
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
                parts.append(" " if self.irrational > 0 else " + ")
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
    
    