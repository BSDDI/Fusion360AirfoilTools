import unittest 
from airfoil_spline.dat_file import AirfoilDatFile, AirfoilPoint, Surfaces


class TestDatFile(unittest.TestCase):
    def test_from_list(self):
        dat = AirfoilDatFile.from_list('test', [[1,0.5], [0.5, 0.5], [0,0], [0.5, -0.5]])
        self.assertEqual(dat.positions[0].surface = Surfaces.TOP)
        self.assertEqual(dat.positions[-1].surface = Surfaces.BTM)