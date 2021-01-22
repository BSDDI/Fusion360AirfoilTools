from enum import Enum
import io
import unittest
import urllib.request
from urllib.error import HTTPError
from .geometry import Point


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

class AirfoilPoint(Point):
    """Point on airfoil. x=0 at leading edge"""
    def __init__(self, x, y, surface = Surfaces.UNKNOWN):
        self.x = x
        self.y = y
        self.surface = surface
            
    def __mul__(self, value):
        return AirfoilPoint(self.x*value, self.y*value, self.surface)

    def __eq__(self, other):
        return self._x == other.x and self._y == other._y

    def __add__(self, other):
        assert isinstance(other, Point)
        return AirfoilPoint(self.x + other.x, self.y + other.y, self.surface)


class AirfoilDatFile(object):
    def __init__(self, name="", positions=False):
        self.name = name
        self.positions = positions

    @staticmethod
    def from_list(self, name, data):
        _positions = []
        last_x = 1.1
        for line in data:
            _positions.append(AirfoilPoint(
                line[0], 
                line[1], 
                Surfaces.TOP if line[0] < last_x else Surfaces.BTM
                )) 
            last_x = _positions[-1].x
        return AirfoilDatFile(_name, _positions)

    @staticmethod
    def from_file(file):      
        last_pos = 1.1
        
        with open(file) as f:
            lines = f.readlines()
    
        _name = lines.pop(0).strip()

        data = []
        for line in lines[1:]:
            data.append(
                ([float(val) for val in f.readline().strip().split()])
            )
        
        AirfoilDatFile.from_list(_name, data)


    
    @staticmethod
    def from_airfoiltools(airfoiltoolsname):
        print("Downloading file from airfoiltools.com")
        try:
            _file = urllib.request.urlretrieve("http://airfoiltools.com/airfoil/seligdatfile?airfoil=" + airfoiltoolsname)
            print("Finished downloading file from airfoiltools.com")
        except HTTPError as ex:
            print("Error downloading file from airfoiltools.com: " + str(ex))
            raise AirfoilNotFound("")
        return AirfoilDatFile.from_file(_file)

    

class TestAirfoilDatFile(unittest.TestCase):
    def setUp(self):
        self._airfoil = AirfoilDatFile.from_file("./examples/naca2412.dat")

    def test_name(self):
        self.assertEqual(self._airfoil.name, "NACA 2414")

    def test_points(self):
        self.assertEqual(self._airfoil._positions[0].x, 1.)
        self.assertEqual(self._airfoil._positions[0].y, 0.00147)
        self.assertEqual(self._airfoil._positions[0].surface, Surfaces.TOP)
        self.assertEqual(self._airfoil._positions[5].surface, Surfaces.TOP)
        self.assertEqual(self._airfoil._positions[-1].surface, Surfaces.BTM)

    def test_download(self):
        _airfoil = AirfoilDatFile("naca2410-il")
        self.assertEqual(_airfoil.name, "NACA 2410")

    def test_not_exist(self):
        with self.assertRaises(AirfoilNotFound):
            _airfoil = AirfoilDatFile("ssss")

if __name__ == "__main__":
    unittest.main()
