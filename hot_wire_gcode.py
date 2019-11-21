from .fusion_connection import fusion, FusionSketch, FusionLoop, FusionPoint
from .geometry import Point, Plane, Line
import io

HOTWIRE_PARAMS = {
    "machine_span": 115.3, # cm
    "cut_rate": 200, # mm/min
}

xy_plane = Plane(Point(0, 0, 0), Point(1, 0, 0))
za_plane = Plane(Point(HOTWIRE_PARAMS["machine_span"], 0, 0), Point(1, 0, 0))


class HotWireGcode(object):
    def __init__(self, component):
        self._base_component = component
        self._edge_profile_1 = FoamEdgeProfile(FusionSketch(self._base_component.sketches["side_1"]))
        self._edge_profile_2 = FoamEdgeProfile(FusionSketch(self._base_component.sketches["side_2"]))
        self._gcode_points = []

    def check_profiles(self):
        return self._edge_profile_1 == self._edge_profile_2

    @property
    def gcode_points(self):
        if not self._gcode_points:
            for point1, point2 in zip(self._edge_profile_1.edge_points, self._edge_profile_2.edge_points):
                self._gcode_points.append(GCode_Point(point1, point2))
        return self._gcode_points        

    def create_gcode_file(self, file, sym = False):
        with io.open(file, 'w') as outf:
            outf.write('G21\n') # millimeters
            outf.write('G94\n') # per minute
            outf.write('G90\n') # absolute movements
            for line in self.gcode_points:
                line.sym = sym
                outf.write(str(line) + '\n') 

    def create_sketches(self):
        sket1a = FusionSketch(self._base_component.create_sketch(
            "points1", 
            self._edge_profile_1.base_sketch.plane
            ))
        sket2a = FusionSketch(self._base_component.create_sketch(
            "points2", 
            self._edge_profile_2.base_sketch.plane
            ))
    
        sketchpoints1 = []
        sketchpoints2 = []

        for gcode_point in self.gcode_points:
            sketchpoints1.append(
                sket1a.create_sketch_point(
                    sket1a.model_to_sketch_space(
                        FusionPoint.from_position(gcode_point.wire_line.start))
                    )
                )
            sketchpoints2.append(
                sket2a.create_sketch_point(
                    sket2a.model_to_sketch_space(
                        FusionPoint.from_position(gcode_point.wire_line.end)
                    )))
            


class GCode_Point(object):
    def __init__(self, point1, point2):
        self._line = Line(point1, point2)
        self._wire_line = None
        self.sym = False

    @property
    def wire_line(self):
        if not self._wire_line:
            self._wire_line = Line(
                xy_plane.line_intersect(self._line),
                za_plane.line_intersect(self._line)
            )
        return self._wire_line

    def __str__(self):
        if self.sym:
            return "G01 F" + str(HOTWIRE_PARAMS["cut_rate"]) + \
                    " X" + str(10*self.wire_line.end.y) + \
                    " Y" + str(10*self.wire_line.end.z) + \
                    " Z" + str(10*self.wire_line.start.y) + \
                    " A" + str(10*self.wire_line.start.z)
        else:            
            return "G01 F" + str(HOTWIRE_PARAMS["cut_rate"]) + \
                    " X" + str(10*self.wire_line.start.y) + \
                    " Y" + str(10*self.wire_line.start.z) + \
                    " Z" + str(10*self.wire_line.end.y) + \
                    " A" + str(10*self.wire_line.end.z)


class FoamEdgeProfile(object):
    def __init__(self, sketch):
        self._base_sketch = sketch
        self._sorted_curves = []
        self._edge_points = []

    @property
    def base_sketch(self):
        return self._base_sketch

    @property
    def sketch_point_machine_zero(self):
        return self._base_sketch.model_to_sketch_space(
            FusionPoint.from_position(Point(self._base_sketch.origin.position.x, 0, 0))
            )
    
    @property
    def sorted_curves(self):
        if not self._sorted_curves:
            self._sorted_curves = FusionLoop.reorder_from_point(
                self.sketch_point_machine_zero, 
                self._base_sketch.profiles[0].outer_loop.sketch_curves
                )
        return self._sorted_curves  # TODO potentially reorder curves too

    def __eq__(self, other):
        return FusionLoop.compare_curve_lists(self.sorted_curves, other.sorted_curves)
    
    @property
    def edge_points(self):
        if not self._edge_points:
            for curve in self.sorted_curves:
                for point in curve.gcode_points:
                    self._edge_points.append(self._base_sketch.sketch_to_model_space(point).position)
        return self._edge_points
