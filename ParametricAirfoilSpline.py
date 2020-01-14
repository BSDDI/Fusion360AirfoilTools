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
    "buddita_wing_centre": ("naca2411-il", 200, 3), 
    "buddita_wing_tip": ("naca2411-il", 120, 3),
    "buddi_wing_centre": ("fx63137-il", 350, 5),
    "buddi_wing_tip": ("fx63137-il", 200, 5),
    "buddi_tail": ("b540ols-il", 263, 5),
    "buddi_fin_root": ("b540ols-il", 233, 5),
    "buddi_fin_tip": ("b540ols-il", 158, 5),
}


def create_new_airfoil():
    doc = FusionDocument(fusion.new_document("test_airfoil"))
    comp = FusionComponent(doc.root_component)
    section = Airfoil("e168-il", 150, 3)
    sketch = FusionSketch(comp.create_sketch("base_section", comp.xy_plane))
    spline = sketch.create_spline(section.modified_positions)
    line = sketch.create_line(spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1))
    sketch_2 = FusionSketch(comp.create_sketch("wing_section", comp.xy_plane))
    sketch_2.project([spline, line])

def update_active_airfoil():

    _section = section_data['buddi_fin_tip']

    comp = FusionComponent.active_component()
    sketch = FusionSketch(comp.sketches["base_section"])
    sketch.clear()

    section = Airfoil(_section[0], _section[1], _section[2])
    spline = sketch.create_spline(section.modified_positions)
    line = sketch.create_line(spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1))

def create_gcode():
    hw = HotWireGcode(FusionComponent.active_component())
    target_file = filedialog.asksaveasfilename()
    hw.create_gcode_file(target_file, False)
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

