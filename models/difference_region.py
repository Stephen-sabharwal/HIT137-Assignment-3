from __future__ import annotations

from math import hypot


class DifferenceRegion:
    """
    Data model for one difference region.
    Encapsulates geometry, type, and found-state.
    """

    __slots__ = ("_x", "_y", "_radius", "_difference_type", "_is_found")

    def __init__(self, x: int, y: int, radius: int, difference_type: str) -> None:
        self._x = int(x)
        self._y = int(y)
        self._radius = int(radius)
        self._difference_type = str(difference_type)
        self._is_found = False

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def radius(self) -> int:
        return self._radius

    @property
    def difference_type(self) -> str:
        return self._difference_type

    @property
    def is_found(self) -> bool:
        return self._is_found

    @is_found.setter
    def is_found(self, value: bool) -> None:
        self._is_found = bool(value)

    def center(self) -> tuple[int, int]:
        return self._x, self._y

    def contains_point(self, px: int, py: int, tolerance: int = 0) -> bool:
        """
        True when click is within the region radius plus tolerance.
        """
        return hypot(px - self._x, py - self._y) <= (self._radius + tolerance)

    def overlaps(self, other: "DifferenceRegion", padding: int = 0) -> bool:
        """
        True when this region overlaps another region (optionally with extra padding).
        """
        min_distance = self._radius + other.radius + padding
        return hypot(self._x - other.x, self._y - other.y) < min_distance
