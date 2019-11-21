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
    hw.create_gcode_file(target_file, True)
    print_toolpaths(hw)
    

def print_toolpaths(hw):
    hw.create_sketches()


def run(context):
    ui = None
    try:

        create_gcode()

        pass
    except:
        if fusion.ui:
            fusion.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

