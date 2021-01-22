from enum import Enum
import io
import unittest
import urllib.request
from urllib.error import HTTPError
import numbers
from math import sin, cos, radians

class DatFileFormats(Enum):
    SELIG=0
    LEDNICER=1

class Surfaces(Enum):
    TOP=0
    BTM=1
    UNKNOWN = 2

class LineReadError(Exception):
    pass

class AirfoilNotFound(Exception):
    pass

last_pos = 1.1

class AirfoilPoint():
    """Point on airfoil. x=0 at leading edge"""
    def __init__(self, x, y, surface = Surfaces.UNKNOWN):
        self.x = x
        self.y = y
        self.surface = surface
            
    def __mul__(self, value):
        if isinstance(value, list):
            return AirfoilPoint(self.x*value[0], self.y*value[1], self.surface)
        elif isinstance(value, numbers.Number):
            return AirfoilPoint(self.x*value, self.y*value, self.surface)

    def __eq__(self, other):
        return self._x == other.x and self._y == other._y

    def __add__(self, other):
        if isinstance(other, AirfoilPoint):
            return AirfoilPoint(self.x + other.x, self.y + other.y, self.surface)
        elif isinstance(other, list):
            return AirfoilPoint(self.x + other[0], self.y + other[1], self.surface)

    def __str__(self):
        return "point x=" + str(self.x) + " y=" + str(self.y) + " surface=" + str(self.surface)

class AirfoilPoints(object):
    def __init__(self, name, positions):
        self.name = name
        self.positions = positions

    @staticmethod
    def from_list(name, data):
        _positions = []
        last_x = 1.1
        for line in data:
            _positions.append(AirfoilPoint(
                line[0], 
                line[1], 
                Surfaces.TOP if line[0] < last_x else Surfaces.BTM
                )) 
            last_x = _positions[-1].x
        return AirfoilPoints(name, _positions)

    @staticmethod
    def from_file(file):      
        last_pos = 1.1
        
        with open(file) as f:
            lines = f.readlines()
    
        data = []
        for line in lines[1:]:
            data.append(
                ([float(val) for val in line.strip().split()])
            )
        
        return AirfoilPoints.from_list(lines.pop(0).strip(), data)

    @staticmethod
    def from_airfoiltools(airfoiltoolsname):
        print("Downloading file from airfoiltools.com")
        try:
            _file = urllib.request.urlretrieve("http://airfoiltools.com/airfoil/seligdatfile?airfoil=" + airfoiltoolsname)
            print("Finished downloading file from airfoiltools.com")
        except HTTPError as ex:
            print("Error downloading file from airfoiltools.com: " + str(ex))
            raise AirfoilNotFound("")
        return AirfoilPoints.from_file(_file[0])

    @property
    def chord(self):
        return self.positions[0].x

    @property
    def te_thickness(self):
        return self.positions[0].y - self.positions[-1].y

    @property
    def thickness(self):
        top=0
        btm=0
        for pos in self.positions:
            if pos.y > top:
                top = pos.y
            if pos.y < btm:
                btm = pos.y
        return top - btm

    def set_props(self, chord, thickness, te_thickness):
        return self.set_chord(chord).set_thickness(thickness).set_te_thickness(te_thickness)

    def set_chord(self, chord):
        x_factor = chord / self.chord
        new_positions = [pos * [x_factor, 1] for pos in self.positions]
        return AirfoilPoints(self.name, new_positions)

    def set_thickness(self, thickness):
        y_factor = thickness / self.thickness
        new_positions = [pos * [1, y_factor] for pos in self.positions]
        return AirfoilPoints(self.name, new_positions) 

    def set_te_thickness(self, te_thickness):
        te_factor = 0.5 * (te_thickness - self.te_thickness) / self.chord

        def _add_thick(pos):
            if pos.surface == Surfaces.TOP:
                return AirfoilPoint(pos.x, pos.y + pos.x * te_factor, pos.surface)
            else:
                return AirfoilPoint(pos.x, pos.y - pos.x * te_factor, pos.surface)
            
        new_positions = [_add_thick(pos) for pos in self.positions]
        
        return AirfoilPoints(self.name, new_positions)

    def set_twist(self, twist):
        ang = radians(twist)
        s = sin(ang)
        c = cos(ang)
        def _rotate(pos):
            return AirfoilPoint(
                pos.x * c - pos.y * s,
                pos.x * s + pos.y * c,
                pos.surface
            )
        return AirfoilPoints(self.name, [_rotate(pos) for pos in self.positions])

    def offset_y(self, yoff):
        return AirfoilPoints(
            self.name,
            [pos + [0, yoff] for pos in self.positions]
        )

    def offset_x(self, xoff):
        return AirfoilPoints(
            self.name,
            [pos + [xoff, 0] for pos in self.positions]
        )
