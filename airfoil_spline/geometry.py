import math
from numbers import Number

class Point(object):
    def __init__(self, x, y, z=0):
        self._x = x
        self._y = y
        self._z = z
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self.x = value

    @property 
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self.y = value

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        self.z = value

    @property
    def array(self):
        return [self._x, self._y, self._z]

    def __mul__(self, other):
        if isinstance(other, Point):
            return Point(x=other.x * self._x, y=other.y * self._y, z=other.z * self._z)
        elif isinstance(other, Number):
            return Point(x=other * self._x, y=other * self._y, z=other * self._z)
        else:
            raise NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Point) or isinstance(other, Number):
            return self.__mul__(other)
        else:
            raise NotImplemented

    def __eq__(self, other):
        return self._x == other.x and self._y == other._y

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(
                x=self.x + other.x,
                y=self.y + other.y,
                z=self.z + other.z
            )
        elif isinstance(other, Number):
            return Point(
                x=self.x + other,
                y=self.y + other,
                z=self.z + other
            )
        else:
            return NotImplemented

    def __str__(self):
        return str(self.array)

    @staticmethod
    def distance(point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2 + (point1.z - point2.z) ** 2)

    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
    
    def __neg__(self):
        return Point(-self._x, -self._y, -self._z)

    @staticmethod
    def dot_product(p1, p2):
        return sum([a * b for a, b in zip(p1.array, p2.array)])
    
    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(
                x=self.x - other.x,
                y=self.y - other.y,
                z=self.z - other.z
            )
        elif isinstance(other, Number):
            return Point(
                x=self.x - other,
                y=self.y - other,
                z=self.z - other
            )
        else:
            return NotImplemented

    @staticmethod
    def cross_product(p1, p2):
        return Point(
            x=p1.y * p2.z - p1.z * p2.y,
            y=p1.z * p2.x - p1.x * p2.z,
            z=p1.x * p2.y - p1.y * p2.x
        )
    
    def set_length(self, value):
        magnitude = self.__abs__()
        return Point(
            x=value * self._x / magnitude,
            y=value * self._y / magnitude,
            z=value * self._z / magnitude
        )

    @property
    def unit(self):
        return self.set_length(1)


class Line(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end
    
    @property
    def start(self):
        return self._start
    
    @property 
    def end(self):
        return self._end

    @property
    def direction(self):
        return Point(
            self._end.x - self._start.x,
            self._end.y - self._start.y,
            self._end.z - self._start.z
            )
    
    @property 
    def length(self):
        return Point.distance(self._end, self._start)  
    
    def distance_to_plane(self, plane):
        return Point.dot_product(plane.origin - self.start, plane.direction.unit) / Point.dot_product(self.direction.unit, plane.direction.unit)


class Plane(object):
    def __init__(self, origin, direction):
        self._origin = origin
        self._direction = direction
    
    @property
    def origin(self):
        return self._origin
    
    @property
    def direction(self):
        return self._direction
    
    def line_intersect(self, line) -> Point:
        return line.start + line.distance_to_plane(self) * line.direction.unit

