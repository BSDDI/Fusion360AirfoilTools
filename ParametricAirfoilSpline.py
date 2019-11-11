#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from enum import Enum
from .airfoil import Airfoil
from .geometry import Point
from .fusion_connection import fusion, FusionDocument, FusionSketch


section_data = {
    "wing_centre": ("naca2411-il", 200, 3),
    "wing_tip": ("naca2411-il", 120, 3),
    "tail_root": ("fx71089a-il", 120, 3),
    "tail_tip": ("fx71089a-il", 100, 3),
}


def create_new_airfoil():
    doc = FusionDocument(fusion.new_document("test_airfoil"))
    section = Airfoil("naca2411-il", 250, 3)
    sketch = FusionSketch(doc.create_sketch("base_section", doc.xy_plane))
    spline = sketch.create_spline(section.modified_positions)
    line = sketch.create_line(spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1))
    sketch_2 = FusionSketch(doc.create_sketch("wing_section", doc.xy_plane))
    sketch_2.project([spline, line])

def update_active_airfoil():
    doc = FusionDocument(fusion.active_document)
    sketch = FusionSketch(doc.sketches["base_section"])
    sketch.clear()

    section = Airfoil("naca2411-il", 210, 3)
    spline = sketch.create_spline(section.modified_positions)
    line = sketch.create_line(spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1))

def run(context):
    ui = None
    try:

        update_active_airfoil()
        pass
    except:
        if fusion.ui:
            fusion.ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

