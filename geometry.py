

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

    def __mul__(self, value):
        return Point(self.x*value, self.y*value, self.z*value)
    
    def __eq__(self, other):
        return self._x == other.x and self._y == other._y

    def __add__(self, other):
        assert isinstance(other, Point)
        return Point(self.x + other.x, self.y + other.y, self.surface)
