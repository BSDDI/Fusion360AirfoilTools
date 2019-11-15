#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from enum import Enum
from .airfoil import Airfoil
from .geometry import Point
from .fusion_connection import fusion, FusionDocument, FusionSketch, FusionComponent, FusionSketchCurve, FusionPoint, FusionLoop

section_data = {
    "wing_centre": ("naca2411-il", 200, 3),
    "wing_tip": ("naca2411-il", 120, 3),
    "tail_root": ("fx71089a-il", 120, 3),
    "tail_tip": ("fx71089a-il", 100, 3),
}


def create_new_airfoil():
    doc = FusionDocument(fusion.new_document("test_airfoil"))
    comp = FusionComponent(doc.root_component)
    section = Airfoil("naca2411-il", 250, 3)
    sketch = comp.create_sketch("base_section", comp.xy_plane)
    spline = sketch.create_spline(section.modified_positions)
    line = sketch.create_line(spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1))
    sketch_2 = FusionSketch(comp.create_sketch("wing_section", comp.xy_plane))
    sketch_2.project([spline, line])

def update_active_airfoil():
    comp = FusionComponent.active_component()
    sketch = FusionSketch(comp.sketches["base_section"])
    sketch.clear()

    section = Airfoil("naca2411-il", 210, 3)
    spline = sketch.create_spline(section.modified_positions)
    line = sketch.create_line(spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1))

def misc_test():
    comp = FusionComponent.active_component()
    sket = FusionSketch(comp.sketches["side_1"])
    sorted_curves = FusionLoop.reorder_from_point(
        sket.model_to_sketch_space(
            FusionPoint.from_position(Point(sket.origin.position.x, 0, 0))
            ), 
        sket.profiles[0].outer_loop.sketch_curves
        )

    sket2 = FusionSketch(comp.sketches["side_2"])
    sorted_curves2 = FusionLoop.reorder_from_point(
        sket2.model_to_sketch_space(
            FusionPoint.from_position(Point(sket2.origin.position.x, 0, 0))
            ), 
        sket2.profiles[0].outer_loop.sketch_curves
        )

    print(FusionLoop.compare_curve_lists(sorted_curves, sorted_curves2))

    points1 = []
    points2 = []
    for curve, curve2 in zip(sorted_curves, sorted_curves2):
        for point, point2 in zip(curve.gcode_points, curve2.gcode_points):
            points1.append(sket.sketch_to_model_space(point))
            points2.append(sket2.sketch_to_model_space(point2))


    #Stuff for checking    
    sket1a = FusionSketch(comp.create_sketch("points1",sket.plane))
    sket2a = FusionSketch(comp.create_sketch("points2", sket2.plane))
    
    sketchpoints1 = []
    sketchpoints2 = []

    for point1, point2 in zip(points1, points2):
        sketchpoints1.append(sket1a.create_sketch_point(sket1a.model_to_sketch_space(point1)))
        sketchpoints2.append(sket2a.create_sketch_point(sket2a.model_to_sketch_space(point2)))
        #print("point1:" + str(point1.position) + " point2:" + str(point2.position))
        
    for point1, point2 in zip(sketchpoints1, sketchpoints2):
        axisInput = comp.component.constructionAxes.createInput()
        axisInput.setByTwoPoints(point1, point2)
        comp.component.constructionAxes.add(axisInput)



def run(context):
    ui = None
    try:

        misc_test()
        pass
    except:
        if fusion.ui:
            fusion.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

