from dataclasses import dataclass

@dataclass
class Vector2f:
    """Class for 2d vector """
    x: float
    y: float
    def __add__(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self + other
