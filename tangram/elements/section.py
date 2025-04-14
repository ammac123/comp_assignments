
from base import LatexElement


class Section(LatexElement):
    def __init__(self, title: str, level: int, content: str, line_number: int = None):
        super().__init__(content, line_number)
        self.title = title
        self.level = level

    def summary(self):
        return f"Section (Level {self.level}): {self.title}"

    def __str__(self):
        return f"Section (Level {self.level}): {self.title}"

    def __repr__(self):
        return f"Section({{Level: {self.level}, Title: {self.title}, ContentSize: [{len(self.content)}}})"