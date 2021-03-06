import adsk.core, adsk.fusion, adsk.cam, traceback
from .geometry import Point, Plane

class Fusion(object):
    def __init__(self):
        self.app = adsk.core.Application.get()
        self.ui  = self.app.userInterface
    
    def new_document(self, name):
        doc = self.app.documents.add(0)
        doc.name = name
        return doc

    @property
    def active_document(self):
        return self.app.activeDocument

    @property
    def open_documents(self):
        return [doc for doc in self.app.documents]

    def object_collection_from_list(self, values):
        coll = adsk.core.ObjectCollection.create()
        for value in values:
            coll.add(value)
        return coll

fusion = Fusion()

class FusionDocument(object):
    def __init__(self, doc):
        self._document = doc
        
    @property
    def root_component(self):
        return self._document.design.rootComponent

    @property
    def active_component(self):
        return self._document.design.activeComponent

    @property
    def sketches(self):
        sketches = {}
        for sketch in self.root_component.sketches:
            sketches[sketch.name] = sketch
        return sketches

    @staticmethod
    def active_document():
        return FusionDocument(fusion.active_document)

class FusionComponent(object):
    def __init__(self, component):
        self._component = component

    @property
    def component(self):
        return self._component

    @property
    def sketches(self):
        sketches = {}
        for sketch in self._component.sketches:
            sketches[sketch.name] = sketch
        return sketches   

    @staticmethod
    def active_component():
        return FusionComponent(FusionDocument.active_document().active_component)

    def create_sketch(self, name, plane):
        sketch = self._component.sketches.add(plane)
        sketch.name = name
        return sketch

    @property
    def xy_plane(self):
        return self._component.xYConstructionPlane
    
    @property
    def xz_plane(self):
        return self._component.xZConstructionPlane
    
    @property
    def yz_plane(self):
        return self._component.yZConstructionPlane
    

class FusionPlane(object):
    def __init__(self, plane):
        self._plane = plane
        self._position = None
    
    def position(self):
        pass


class FusionSketch(object):
    def __init__(self, sketch):
        self._sketch = sketch
        self._profiles = []

    def create_point(self, location):
        if isinstance(location, list):
            return [self.create_point(loc) for loc in location]
        elif isinstance(location, Point):
            return adsk.core.Point3D.create(0.1 * location.x, 0.1 * location.y, 0)
        else:
            raise TypeError("Expected a Point or list[Point]")
    
    def create_sketch_point(self, fusion_point):
        return self._sketch.sketchPoints.add(fusion_point.point)

    def create_spline(self, locations):
        point_collection = fusion.object_collection_from_list(self.create_point(locations))
        return self._sketch.sketchCurves.sketchFittedSplines.add(point_collection)

    def create_line(self, start, end):
        if isinstance(start, Point) and isinstance(end, Point):
            return self.create_line(self.create_point(start), self.create_point(end))
        elif isinstance(start, adsk.fusion.SketchPoint) and isinstance(end, adsk.fusion.SketchPoint):
            return self._sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
        else:
            raise TypeError("Expected two geometry.Point objects or two adsk.core.Point3D objects")

    def delete_item(self, item):
        if isinstance(item, list):
            for it in item:
                self.delete_item(it)
        else:
            item.deleteMe()

    def clear(self):
        while self._sketch.sketchCurves.count > 0:
            self._sketch.sketchCurves.item(0).deleteMe()

    def project(self, items):
        if isinstance(items, list):
            return [self.project(item) for item in items]
        else:
            return self._sketch.project(items)

    @property
    def plane(self):
        return self._sketch.referencePlane

    @property
    def curves(self):
        return [curve for curve in self._sketch.sketchCurves]

    @property
    def sketch_curves(self):
        return [FusionSketchCurve(curve) for curve in self.curves]

    @property
    def output_sketch_curves(self):
        return [curve for curve in self.sketch_curves if not curve.is_construction]

    @property
    def profiles(self):
        if not self._profiles:
            self._profiles = [FusionProfile(profile) for profile in self._sketch.profiles]
        return self._profiles

    def model_to_sketch_space(self, point):
        return FusionPoint(self._sketch.modelToSketchSpace(point.point))

    def sketch_to_model_space(self, point):
        return FusionPoint(self._sketch.sketchToModelSpace(point.point))

    @property
    def origin(self): 
        return FusionPoint(self._sketch.origin)

class FusionProfile(object):
    def __init__(self, profile):
        self._profile = profile
        self._loops = []

    @property
    def loops(self):
        if not self._loops:
            self._loops = [FusionLoop(loop) for loop in self._profile.profileLoops]
        return self._loops

    @property
    def outer_loop(self):
        for loop in self.loops:
            if loop.is_outer:
                return loop
    

class FusionLoop(object):
    def __init__(self, loop):
        self._loop = loop
        self._sketch_curves = []

    @property
    def sketch_curves(self):
        if not self._sketch_curves:
            self._sketch_curves = [FusionSketchCurve(curve.sketchEntity) for curve in self._loop.profileCurves]
        return self._sketch_curves

    @property
    def is_outer(self):
        return self._loop.isOuter

    @staticmethod
    def reorder_from_point(target_start_point, curve_list):
        new_start_curve_id = FusionLoop.closest_curve_id(target_start_point, curve_list)
        new_curve_list = []
        for i in range(new_start_curve_id, len(curve_list)):
            new_curve_list.append(curve_list[i])
        for i in range(0, new_start_curve_id):
            new_curve_list.append(curve_list[i])
        return new_curve_list

    @staticmethod
    def closest_curve_id(target_point, curve_list):
        output_curve_id = 0
        min_distance = Point.distance(curve_list[0].start_point.position, target_point.position)
        for i, curve in enumerate(curve_list[1:], 1):
            check_dist = Point.distance(curve.start_point.position, target_point.position)
            if check_dist < min_distance:
                min_distance = check_dist
                output_curve_id = i
        return output_curve_id

    @staticmethod
    def compare_curve_lists(list1, list2):
        if len(list1) != len(list2): return False
        for curve1, curve2 in zip(list1, list2):
            if curve1.curve_type != curve2.curve_type: return False
        return True

class FusionSketchCurve(object):
    def __init__(self, curve):
        self._curve = curve
        self._parametric_range=[]

    @property
    def length(self):
        return self._curve.length

    @property
    def curve_type(self):
        return self._curve.objectType

    @property
    def is_construction(self):
        return self._curve.isConstruction

    def __str__(self):
        return "curve, length = " + str(self.length) + ", type = " + self.curve_type

    @property
    def start_point(self):
        return FusionPoint(self._curve.startSketchPoint.geometry)
    
    @property
    def end_point(self):
        return FusionPoint(self._curve.endSketchPoint.geometry)
    
    @property
    def gcode_points(self):
        if self.curve_type == "adsk::fusion::SketchLine":
            return [self.start_point, self.end_point]
        else:
            return self.parametric_points(50)

    def parametric_points(self, npoints):
        points = []
        #returnValue, startPoint, endPoint = self._curve.getEndPoints()
        
        start_param = self.parametric_range[0]

        for i in range(0, npoints):
            new_param = self._curve.geometry.evaluator.getParameterAtLength(start_param, i * self.length / (npoints - 1))[1]
            new_point = self.parametric_point(new_param)
            points.append(new_point)
        return points

    def parametric_point(self, param):
        print(param)
        new_point3d = self._curve.geometry.evaluator.getPointAtParameter(param)
        if new_point3d[0]:
            return FusionPoint(new_point3d[1])
        else:
            return None

    @property
    def parametric_range(self):
        if not self._parametric_range:
            param_range = self._curve.geometry.evaluator.getParameterExtents()
            if not param_range[0]:
                self._parametric_range = [0, 0]
            else:
                self._parametric_range = param_range[1:]
        return self._parametric_range



class FusionPoint(object):
    def __init__(self, point):
        self._point = point
        self._position = Point(self._point.x, self._point.y, self._point.z)

    def __str__(self):
        return "FusionPoint location = " + str(self._position)

    @property
    def point(self):
        return self._point

    @property
    def position(self):
        return self._position

    @staticmethod
    def from_position(position):
        point3d = adsk.core.Point3D.create(position.x, position.y, position.z)
        return FusionPoint(point3d)
