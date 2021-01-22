from .dat_file import AirfoilDatFile, Surfaces
from .geometry import Point
import unittest

class Airfoil(object):
    def __init__(self, airfoiltoolsnameorfile, chord, te_thickness, fromfile=False):
        self._raw_data = AirfoilDatFile(airfoiltoolsnameorfile, fromfile)
        self._chord = chord
        self._te_thickness = te_thickness
        self._modified_positions = []

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def modified_positions(self):
        if not self._modified_positions:
            self._modified_positions = [self._transform_point(pos) for pos in self._raw_data.positions]
        return self._modified_positions

    def _transform_point(self, in_point):
        return self._apply_te_thickness(self._apply_chord(in_point))

    def _apply_chord(self, in_point):
        return in_point * self._chord
    
    def _apply_te_thickness(self, in_point):
        add_thick = 0.5 * self._te_thickness * in_point.x / self._chord
        if in_point.surface == Surfaces.TOP:
            out_point = in_point + Point(0, add_thick)
        elif in_point.surface == Surfaces.BTM:
            out_point = in_point + Point(0, -add_thick)
        out_point.surface = in_point.surface
        return out_point

if __name__ == "__main__":
    section = Airfoil("naca2411-il", 100, 3)
    print(section._modified_positions)