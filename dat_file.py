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

class AirfoilPoint(Point):
    def __init__(self, x, y, surface = Surfaces.UNKNOWN):
        self._x = x
        self._y = y
        self._surface = surface
    
    @staticmethod
    def from_dat_line(dat_line):
        simple = dat_line.strip().split()
        try:
            return AirfoilPoint(float(simple[0]), float(simple[1]))
        except:
            raise LineReadError
        

    def __mul__(self, value):
        return AirfoilPoint(self.x*value, self.y*value, self.surface)

    def __eq__(self, other):
        return self._x == other.x and self._y == other._y

    def __add__(self, other):
        assert isinstance(other, Point)
        return AirfoilPoint(self.x + other.x, self.y + other.y, self.surface)

    @property
    def surface(self):
        return self._surface
    
    @surface.setter
    def surface(self, value):
        self._surface = value

class AirfoilDatFile(object):
    def __init__(self, airfoiltoolsname=""):
        self._airfoiltoolsname = airfoiltoolsname
        self._file = ""
        self._name = ""
        self._format = DatFileFormats.SELIG
        self._positions=[]
        if self._airfoiltoolsname:
            self._read_file()

    def _read_file(self):       
        with open(self.file) as f:
            lines = f.readlines()

        self._name = lines.pop(0).strip()
        for line in lines:
            try:
                self._positions.append(AirfoilPoint.from_dat_line(line))
                if len(self._positions) > 1:
                    if self._positions[-2].x > self._positions[-1].x:
                        self._positions[-1].surface = Surfaces.TOP
                    else:
                        self._positions[-1].surface = Surfaces.BTM
                else:
                    self._positions[0].surface = Surfaces.TOP
            except LineReadError:
                pass
    
    @staticmethod
    def download_airfoil_file(airfoiltoolsname):
        print("Downloading file from airfoiltools.com")
        try:
            _file = urllib.request.urlretrieve("http://airfoiltools.com/airfoil/seligdatfile?airfoil=" + airfoiltoolsname)
            print("Finished downloading file from airfoiltools.com")
        except HTTPError as ex:
            print("Error downloading file from airfoiltools.com: " + str(ex))
            raise AirfoilNotFound("")
        return _file

    @property
    def file(self):
        if not self._file:
            self._file = AirfoilDatFile.download_airfoil_file(self._airfoiltoolsname)[0]
        return self._file

    @file.setter
    def file(self, value):
        self.__init__("")
        self._file = value
        self._read_file()

    @property
    def airfoiltoolsname(self):
        return self._airfoiltoolsname

    @airfoiltoolsname.setter
    def airfoiltoolsname(self, value):
        self.__init__(value)
        
    @property
    def name(self):
        return self._name

    @property
    def positions(self):
        return self._positions

    @staticmethod
    def from_file(file):
        _airfoil = AirfoilDatFile()
        _airfoil.file = file
        return _airfoil


    

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
