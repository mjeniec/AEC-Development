
# PYTHON NODE 01 # # 

import clr

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)

lines = UnwrapElement(IN[0])

footprint_lines = []
ridge_lines = []

for line in lines:
    
    try:
    
        style_name = line.LineStyle.Name
        
        if style_name == "Roof Slope Solver - Footprint":
            
            curve = line.GeometryCurve 
            
            start = curve.GetEndPoint(0)
            end = curve.GetEndPoint(1)
            
            footprint_lines.append({
                "model_line": line,
                "geometry_curve": curve,
                "start_point": start,
                "end_point": end,
                "elevation": start.Z
            }) 
        
        elif style_name == "Roof Slope Solver - Ridge":
            
            curve = line.GeometryCurve
            
            start = curve.GetEndPoint(0)
            end = curve.GetEndPoint(1)
            
            ridge_lines.append({
                "model_line": line, 
                "geometry_curve" : curve,
                "start_point" : start,
                "end_point" : end,
                "elevation" : start.Z
            })
            
    except Exception as e:
         print(e)
    
OUT = footprint_lines, ridge_lines


             
        
# # PYTHON NODE 02 # #

#DUMMY DATA FOR TESTING #

footprint_lines = [
    {
        "model_line": "ML1",
        "geometry_curve": "GC1",
        "start_point": (0, 0, 0),
        "end_point": (8000, 0, 0),
        "elevation": 0
    },
    {
        "model_line": "ML2",
        "geometry_curve": "GC2",
        "start_point": (8000, 4000, 0),
        "end_point": (8000, 0, 0),
        "elevation": 0
    },
    {
        "model_line": "ML3",
        "geometry_curve": "GC3",
        "start_point": (0, 4000, 0),
        "end_point": (8000, 4000, 0),
        "elevation": 0
    },
    {
        "model_line": "ML4",
        "geometry_curve": "GC4",
        "start_point": (0, 0, 0),
        "end_point": (0, 4000, 0),
        "elevation": 0
    }
]

ridge_lines = [
    {
        "model_line": "RL1",
        "geometry_curve": "RGC1",
        "start_point": (2500, 2000, 2500),
        "end_point": (5500, 2000, 2500),
        "elevation": 2500
    }
]

from Autodesk.Revit.DB import *
import math

footprint_lines, ridge_lines = IN[0]

def distance(point_1, point_2):
    return point_1.DistanceTo(point_2)

def calculate_angle(roof_s, roof_e, ridge_point):

    edge_vector = roof_e.Subtract(roof_s)
    ridge_vector = ridge_point.Subtract(roof_s)

    normal = edge_vector.CrossProduct(ridge_vector)

    if normal.Z < 0:
        normal = normal.Negate()

    roof_angle = normal.AngleTo(XYZ.BasisZ)

    return roof_angle
    

roof_surfaces = []

for edge in footprint_lines:

    roof_surfaces.append({
        "model_line": edge["model_line"], 
        "geometry_curve" : edge["geometry_curve"],
        "start_point" : edge["start_point"],
        "end_point" : edge["end_point"],
        "elevation" : edge["elevation"]
    })

for roof in roof_surfaces:
    # if only one ridge & ridge a single straight line
    ridge_s =(ridge_lines[0]["start_point"]) # (2500, 2000, 2500)
    ridge_e = (ridge_lines[0]["end_point"]) # (5500, 2000, 2500)

    roof_s = roof["start_point"]
    roof_e = roof["end_point"]

    # FUTURE FUNCTION:
    roof_s_to_ridge_s = distance(roof_s, ridge_s)
    roof_s_to_ridge_e = distance(roof_s, ridge_e)

    ridge_opt1 = ridge_s if roof_s_to_ridge_s < roof_s_to_ridge_e else ridge_e


    roof_e_to_ridge_s = distance(roof_e, ridge_s)
    roof_e_to_ridge_e = distance(roof_e, ridge_e)

    ridge_opt2 = ridge_s if roof_e_to_ridge_s < roof_e_to_ridge_e else ridge_e


    roof["ridge_points"] = [ridge_opt1] if ridge_opt1 == ridge_opt2 else [ridge_opt1, ridge_opt2]
    

for roof in roof_surfaces:

    ridge_point = roof["ridge_points"][0]
    roof_s = roof["start_point"]
    roof_e = roof["end_point"]
    
    roof["roof_angle"] = calculate_angle(roof_s, roof_e, ridge_point)
     

OUT = roof_surfaces


# # PYTHON NODE 03 # # 

import clr
import math

clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)


doc = DocumentManager.Instance.CurrentDBDocument


# INPUTS
# IN[0] = roof_surfaces from Python Node 2
# IN[1] = Revit Level
# IN[2] = Revit RoofType

roof_surfaces = IN[0]
roof_level = UnwrapElement(IN[1])
roof_type = UnwrapElement(IN[2])


# Create the closed roof footprint from the original curves
footprint = CurveArray()

for roof_surface in roof_surfaces:
    footprint.Append(roof_surface["geometry_curve"])


TransactionManager.Instance.EnsureInTransaction(doc)

try:
    # Revit fills this with the new roof's boundary ModelCurves
    model_curve_mapping = ModelCurveArray()

    result = doc.Create.NewFootPrintRoof(
        footprint,
        roof_level,
        roof_type,
        model_curve_mapping
    )

    # In Dynamo CPython, the method returns:
    # (new roof, populated ModelCurveArray)
    new_roof = result[0]
    model_curve_mapping = result[1]

    # Convert ModelCurveArray into a normal Python list
    roof_boundary_curves = []

    iterator = model_curve_mapping.ForwardIterator()
    iterator.Reset()

    while iterator.MoveNext():
        roof_boundary_curves.append(iterator.Current)

    # Apply the calculated slope to each corresponding roof edge
    for roof_surface, roof_boundary_curve in zip(
        roof_surfaces,
        roof_boundary_curves
    ):
        roof_angle = roof_surface["roof_angle"]

        # Revit expects slope as rise/run, not an angle
        slope = math.tan(roof_angle)

        new_roof.set_DefinesSlope(
            roof_boundary_curve,
            True
        )

        new_roof.set_SlopeAngle(
            roof_boundary_curve,
            slope
        )

    TransactionManager.Instance.TransactionTaskDone()

    OUT = new_roof

except Exception as error:
    TransactionManager.Instance.ForceCloseTransaction()
    OUT = str(error)