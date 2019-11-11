import adsk.core, adsk.fusion, adsk.cam, traceback
from .geometry import Point

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
        self._root_component = self._document.design.rootComponent
        
    def create_sketch(self, name, plane):
        sketch = self._root_component.sketches.add(plane)
        sketch.name = name
        return sketch
    
    @property
    def xy_plane(self):
        return self._root_component.xYConstructionPlane
    
    @property
    def xz_plane(self):
        return self._root_component.xZConstructionPlane
    
    @property
    def yz_plane(self):
        return self._root_component.yZConstructionPlane
    
    @property
    def sketches(self):
        sketches = {}
        for sketch in self._root_component.sketches:
            sketches[sketch.name] = sketch
        return sketches

class FusionSketch(object):
    def __init__(self, sketch):
        self._sketch = sketch
    
    def create_point(self, location):
        if isinstance(location, list):
            return [self.create_point(loc) for loc in location]
        elif isinstance(location, Point):
            return adsk.core.Point3D.create(0.1 * location.x, 0.1 * location.y, 0)
        else:
            raise TypeError("Expected a Point or list[Point]")

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