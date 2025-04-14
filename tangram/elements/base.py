from abc import ABC, abstractmethod


class LatexElement(ABC):
    def __init__(self, content: str, line_number: int = None):
        self.content = content
        self.line_number = line_number

    def summary(self) -> str:
        """Description of the element"""
        pass

    def __str__(self):
        return self.summary()

    def __len__(self):
        return len(self.content)