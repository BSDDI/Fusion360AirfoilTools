#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
from .airfoil_points import AirfoilPoints

section_data = {
    "buddita_wing_centre": ("naca2411-il", 200, 3), 
    "buddita_wing_tip": ("naca2411-il", 120, 3),
    "buddi_wing_centre": ("fx63137-il", 350, 5),
    "buddi_wing_tip": ("fx63137-il", 200, 5),
    "buddi_tail": ("b540ols-il", 263, 5),
    "buddi_fin_root": ("b540ols-il", 233, 5),
    "buddi_fin_tip": ("b540ols-il", 158, 5),
    "naca0012": ("naca0018-il", 600, 5)
}

app = adsk.core.Application.get()

def object_collection_from_list(values):
    coll = adsk.core.ObjectCollection.create()
    for value in values:
        coll.add(value)
    return coll

def create_document(name):
    doc = app.documents.add(0)
    doc.name = name
    return doc, doc.design.rootComponent

def create_xy_plane(component, offset):
    planeinput = component.constructionPlanes.createInput()
    offsetValue = adsk.core.ValueInput.createByReal(offset)
    planeinput.setByOffset(component.xYConstructionPlane, offsetValue)
    return component.constructionPlanes.add(planeinput)

def create_sketch(component, plane, name):
    sketch = component.sketches.add(plane)
    sketch.name = name
    return sketch

def create_point(x,y,z):
    return adsk.core.Point3D.create(0.1 * x, 0.1 * y, z)

def create_points(points):
    return object_collection_from_list(
        [create_point(pos.x, pos.y, 0) for pos in points]
    )

def create_new_airfoil_sketch(component, plane, afpoints):
    sketch = create_sketch(component, plane, "base_section")

    spline = sketch.sketchCurves.sketchFittedSplines.add(
        create_points(afpoints.positions)
    )

    te_line = sketch.sketchCurves.sketchLines.addByTwoPoints(
        spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1)
    )

    return sketch
    #sketch2 = create_sketch(comp, comp.xYConstructionPlane, "wing_section")
    #sketch2.project(spline)
    #sketch2.project(te_line)

def create_new_airfoil_doc(afpoints):
    doc, comp = create_document(afpoints.name)
    sketch = create_new_airfoil_sketch(comp, comp.xYConstructionPlane, afpoints.name)

def create_new_panel_doc(panelcsv, affile):
    afpoints = AirfoilPoints.from_file(affile)

    doc, comp = create_document('paneltest')
    secs=[]
    with open(panelcsv) as f:
        cols=f.readline().split(',')
        for line in f.readlines():
            secs.append(
                {col.strip(): float(val.strip()) for col,val in zip(cols, line.split(','))}
            )
    
    for id, sec in enumerate(secs):
        sketch = create_new_airfoil_sketch(
            comp, 
            create_xy_plane(comp, 0.1 * sec['zoff']), 
            afpoints.set_chord(
                sec['chord']
            ).set_thickness(
                sec['thickness']
            ).set_te_thickness(
                sec['te_thickness']
            ).set_twist(
                sec['twist']
            ).offset_y(
                sec['yoff']
            ).offset_x(
                sec['xoff']
            )
        )
        sketch.saveAsDXF('C://Users//td6834//projects//bird//' + 'section_' + str(id) + '.dxf')



def run(context):
    try:

        #airfoil = AirfoilPoints.from_file(
        #    "C://Users//td6834//AppData//Roaming//Autodesk//Autodesk Fusion 360//API//Scripts//ParametricAirfoilSpline//test//test_airfoil.dat"
        #).set_chord(100).set_thickness(10).set_te_thickness(1).set_twist(-5).offset_x(10).offset_y(20)
        
        create_new_panel_doc(
            "C://Users//td6834//projects//bird//birdwingpanels.csv",
            "C://Users//td6834//projects//bird//pw075.dat"
        )
#        create_new_airfoil_doc(airfoil)

        pass
    except:
        if app.userInterface:
            app.userInterface.messageBox('Failed:\n{}'.format(traceback.format_exc()))



#def update_active_airfoil():
#
#    _section = section_data['naca0012']

#    comp = FusionComponent.active_component()
#    sketch = FusionSketch(comp.sketches["base_section"])
#    sketch.clear()#

#    section = Airfoil(_section[0], _section[1], _section[2])
#    spline = sketch.create_spline(section.modified_positions)
#    line = sketch.create_line(spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1))

#def create_gcode():
#    hw = HotWireGcode(FusionComponent.active_component())
#    target_file = filedialog.asksaveasfilename()
#    hw.create_gcode_file(target_file, True)
#    print_toolpaths(hw)
    

#def print_toolpaths(hw):
#    hw.create_sketches()#

