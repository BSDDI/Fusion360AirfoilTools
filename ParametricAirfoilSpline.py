#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from enum import Enum
from .airfoil import Airfoil
from .geometry import Point
from .fusion_connection import fusion, FusionDocument, FusionSketch, FusionComponent, FusionSketchCurve, FusionPoint, FusionLoop
from .hot_wire_gcode import HotWireGcode, xy_plane, za_plane
from tkinter import filedialog

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

def create_gcode():
    hw = HotWireGcode(FusionComponent.active_component())
    target_file = filedialog.asksaveasfilename()
    hw.create_gcode_file(target_file)


def print_toolpaths(hw):
    #Stuff for checking    
    sket1a = FusionSketch(comp.create_sketch("points1", xy_plane))
    sket2a = FusionSketch(comp.create_sketch("points2", za_plane))
    
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

        create_gcode()
        pass
    except:
        if fusion.ui:
            fusion.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

