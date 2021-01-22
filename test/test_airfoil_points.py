import unittest 
from airfoil_points import AirfoilPoints, AirfoilPoint, Surfaces


class TestDatFile(unittest.TestCase):
    def test_from_list(self):
        dat = AirfoilPoints.from_list('test', [[1,0.5], [0.5, 0.5], [0,0], [0.5, -0.5]])
        self.assertEqual(dat.positions[0].surface, Surfaces.TOP)
        self.assertEqual(dat.positions[-1].surface, Surfaces.BTM)

    def test_from_file(self):
        dat = AirfoilPoints.from_file('test//test_airfoil.dat')
        self.assertEqual(dat.positions[0].surface, Surfaces.TOP)
        self.assertEqual(dat.positions[-1].surface, Surfaces.BTM)

    def test_measurements(self):
        dat = AirfoilPoints.from_file('test//test_airfoil.dat')
        self.assertEqual(dat.chord, 1)
        self.assertEqual(dat.te_thickness, dat.positions[0].y - dat.positions[-1].y)
        self.assertEqual(dat.thickness, 0.14121)

    def test_set_chord(self):
        dat = AirfoilPoints.from_file('test//test_airfoil.dat').set_chord(2)
        self.assertEqual(dat.chord, 2)

    def test_set_thick(self):
        dat = AirfoilPoints.from_file('test//test_airfoil.dat').set_thickness(0.5)
        self.assertEqual(dat.thickness, .5)

    def test_set_te_thick(self):
        dat = AirfoilPoints.from_file('test//test_airfoil.dat').set_te_thickness(0.1)
        self.assertEqual(dat.te_thickness, .1)

    def test_from_airfoiltools(self):
        dat = AirfoilPoints.from_airfoiltools('naca2411-il')
        self.assertEqual(dat.chord, 1)

if __name__ == "__main__":
    unittest.main()