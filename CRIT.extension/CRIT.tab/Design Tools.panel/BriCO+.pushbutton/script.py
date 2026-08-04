# -*- coding: utf-8 -*-
# Brick Coordinator readable router v8
# Generated from the working v7 router, expanded so the two engines are readable/editable.

# ==============================================================================
# FUTURE IMPROVEMENT - ACTIVE VIEW VALIDATION
# ==============================================================================
#
# This tool creates temporary Detail Lines using:
#     doc.Create.NewDetailCurve(doc.ActiveView, ...)
#
# Detail Lines are view-specific annotation and cannot be created in every
# view type (e.g. a standard 3D view).
#
# Before running the main tool, check that the active view supports Detail
# Curves. If not, inform the user and exit gracefully.
#
# Example behaviour:
#
# if not active_view_supports_detail_lines:
#     UI.TaskDialog.Show(
#         "Brick Layout",
#         "Please run this tool from a Floor Plan, Ceiling Plan, Section or "
#         "Elevation view."
#     )
#     script.exit()
#
# Future learning:
# - Investigate which View classes/types support Detail Curves.
# - Learn how to query the active view type through the Revit API.
# ==============================================================================

import math
import copy
from pyrevit import revit, UI, script
from Autodesk.Revit.DB import *
from System.Collections.Generic import List

# Import native .NET presentation frameworks safely
import clr
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")

# Use direct programmatic layout instantiation to stay completely clear of broken XAML compilers
from System.Windows import Window, WindowStartupLocation, Thickness, HorizontalAlignment, FontWeights
from System.Windows.Controls import StackPanel, TextBlock, Grid, Button, ColumnDefinition

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def extract_wall_boundary_loops(walls):

    # Extracted thickness from the first wall instance safely
    # Note: consider walls of varying thickness
    wall_thickness_feet = walls[0].WallType.Width

    # 1. Fuse ALL wall solids to dissolve butt joints and calculate corners
    geo_options = Options() # Creates a Revit geometry settings object.
    geo_options.ComputeReferences = False
    geo_options.DetailLevel = ViewDetailLevel.Fine # Give me most detailed (Fine) version of geometry
    master_solid = None # create empty variable to eventually store fused solid

    for wall in walls:
        geo_elem = wall.get_Geometry(geo_options) # returns geometry element, NOT just solid (therefore need following loop)
        if geo_elem is None:
            continue
        for geo_obj in geo_elem: # look through everything in geomtry element container 
            if isinstance(geo_obj, Solid) and geo_obj.Volume > 0: # take the proper solids with volume (not curves or edges)
                if master_solid is None: # take first valid solid and store in master_solid
                    master_solid = geo_obj 
                else:
                    try:  # try and fuse subsequent solids found with master_solid
                        master_solid = BooleanOperationsUtils.ExecuteBooleanOperation(
                            master_solid, geo_obj, BooleanOperationsType.Union
                        )
                    except Exception:
                        pass

    if master_solid is None:
        UI.TaskDialog.Show("Error", "Could not generate a fused solid geometry from walls.")
        script.exit()

    # 2. Extract the profile loops from the downward-facing bottom face
    all_loops = []
    for face in master_solid.Faces:
        if isinstance(face, PlanarFace) and face.FaceNormal.IsAlmostEqualTo(XYZ(0, 0, -1)):
            for loop in face.GetEdgesAsCurveLoops():
                all_loops.append(loop)
            break

    if not all_loops:
        UI.TaskDialog.Show("Error", "No bottom face profile found on the fused wall geometry.")
        script.exit()

    return all_loops, wall_thickness_feet

def shape_detection_and_track_separation(all_loops, wall_thickness_feet):

    lines_side_a = []
    lines_side_b = []

    if len(all_loops) == 1: # i.e if open loop wall
        is_closed_loop_layout = False
        print("Morphology Identified: Open String. Splitting parallel tracks topologically...")

        selected_loop = all_loops[0]
        # Convert the CurveLoop container into an iterable list of individual Curve objects
        loop_curves = [c for c in selected_loop] 
        
        # Find the indices of the end-caps matching the wall thickness
        cap_indices = []
        for idx, curve in enumerate(loop_curves):
            if abs(curve.Length - wall_thickness_feet) < 0.083: # 1-inch variance tolerance
                cap_indices.append(idx)
       
        if len(cap_indices) != 2:
            UI.TaskDialog.Show("Geometry Error", "Could not identify the two wall end caps.")
            script.exit()

        cap_indices.sort() # sort indices into ascending order 
        idx1 = cap_indices[0]
        idx2 = cap_indices[1]

        # Extract the two long continuous tracks sitting between the end caps
        track_1 = loop_curves[idx1 + 1 : idx2] # gives all curves between first cap and second cap
        track_2 = loop_curves[idx2 + 1 :] + loop_curves[:idx1] # gives curves from second cap to end of the list and everything before cap 1

        # Remove any remaining cap curves by filtering out curves
        # whose length is approximately equal to the wall thickness.
        lines_side_a = [c for c in track_1 if abs(c.Length - wall_thickness_feet) >= 0.083]
        lines_side_b = [c for c in track_2 if abs(c.Length - wall_thickness_feet) >= 0.083]

    else: # i.e if closed loop wall
        is_closed_loop_layout = True
        print("Morphology Identified: Closed Loop. Preparing both perimeter loops for user confirmation.")

        if len(all_loops) != 2:
            UI.TaskDialog.Show( 
                "Geometry Error",
                "Expected exactly two perimeter loops for a closed wall layout."
            )
            script.exit()

        lines_side_a = [c for c in all_loops[0]]
        lines_side_b = [c for c in all_loops[1]]
        
    if not lines_side_a or not lines_side_b:
        UI.TaskDialog.Show("Geometry Error", "Could not split the profile loop into distinct tracks.")
        script.exit()

    # TODO: Separate geometry validation from UI error handling.
    # Consider raising descriptive exceptions here and handling
    # TaskDialog display and script termination in the caller.

    return lines_side_a, lines_side_b, is_closed_loop_layout

def confirm_exterior_track(lines_side_a, doc, uidoc):
                                             
    created_line_ids = []
    thick_override = OverrideGraphicSettings()
    thick_override.SetProjectionLineColor(Color(255, 0, 255)) # Hot Pink (Magenta)
    thick_override.SetProjectionLineWeight(4)

    t_draw = Transaction(doc, "Draw Temp Track Highlight")
    t_draw.Start()

    for curve in lines_side_a:
        try:
            p_start = curve.GetEndPoint(0)
            p_end = curve.GetEndPoint(1)
            view_curve = Line.CreateBound(XYZ(p_start.X, p_start.Y, 0), XYZ(p_end.X, p_end.Y, 0))
            d_line = doc.Create.NewDetailCurve(doc.ActiveView, view_curve) # returns a revit element (i.e a new Detail Curve)
            created_line_ids.append(d_line.Id)
            doc.ActiveView.SetElementOverrides(d_line.Id, thick_override)
        except Exception:
            pass
    t_draw.Commit()

    # -------------------------------------------------------------------------
    # TODO - Investigate why new XYZ objects are created with Z = 0 before
    # Line.CreateBound().
    #
    # Current understanding:
    # - p_start and p_end are already valid XYZ objects returned by
    #   Curve.GetEndPoint().
    # - The code rebuilds these as new XYZs using the same X/Y coordinates
    #   but forces Z = 0.
    #
    # Questions to investigate:
    # 1. Would Line.CreateBound(p_start, p_end) work directly?
    # 2. Does NewDetailCurve require the curve to lie on the active view's
    #    sketch plane?
    # 3. If so, should the Z coordinate come from the active view's level
    #    rather than being hardcoded to 0?
    #
    # Test by replacing:
    #     Line.CreateBound(
    #         XYZ(p_start.X, p_start.Y, 0),
    #         XYZ(p_end.X, p_end.Y, 0)
    #     )
    # with:
    #     Line.CreateBound(p_start, p_end)
    # and observe whether Revit accepts the detail curve or throws a
    # "curve must be in plane" type error.
    # -------------------------------------------------------------------------


    uidoc.Selection.SetElementIds(List[ElementId]())
    uidoc.RefreshActiveView()

    # Pure Programmatic WPF Windows Object Generation
    panel = Window()
    panel.Title = "Track Selector"
    panel.Height = 150
    panel.Width = 420
    panel.WindowStartupLocation = WindowStartupLocation.CenterScreen
    panel.Topmost = True
    panel.ResizeMode = panel.ResizeMode.NoResize

    main_layout = StackPanel()
    main_layout.Margin = Thickness(15)

    txt_lbl = TextBlock()
    txt_lbl.Text = "Is the PINK HIGHLIGHTED track the EXTERIOR side?"
    txt_lbl.FontWeight = FontWeights.Bold
    txt_lbl.FontSize = 13
    txt_lbl.TextWrapping = txt_lbl.TextWrapping.Wrap
    txt_lbl.Margin = Thickness(0, 0, 0, 15)
    main_layout.Children.Add(txt_lbl)

    btn_grid = Grid()
    col1 = ColumnDefinition()
    col2 = ColumnDefinition()
    btn_grid.ColumnDefinitions.Add(col1)
    btn_grid.ColumnDefinitions.Add(col2)

    state = {"approved": True}
    # TODO: Decide how closing the dialog without selecting Yes or No should be handled.

    def click_yes(sender, e):
        state["approved"] = True
        panel.Close()

    def click_no(sender, e):
        state["approved"] = False
        panel.Close()

    btn_yes = Button()
    btn_yes.Content = "Yes, Use Highlighted Track"
    btn_yes.Height = 30
    btn_yes.Margin = Thickness(0, 0, 5, 0)
    btn_yes.Click += click_yes
    Grid.SetColumn(btn_yes, 0)
    btn_grid.Children.Add(btn_yes)

    btn_no = Button()
    btn_no.Content = "No, Use Opposite Track"
    btn_no.Height = 30
    btn_no.Margin = Thickness(5, 0, 0, 0)
    btn_no.Click += click_no
    Grid.SetColumn(btn_no, 1)
    btn_grid.Children.Add(btn_no)

    main_layout.Children.Add(btn_grid)
    panel.Content = main_layout
    panel.ShowDialog()

    user_selection_is_side_a = state["approved"]

    t_clean = Transaction(doc, "Clean Temp Highlights")
    t_clean.Start()
    for l_id in created_line_ids: # created at beginning of D
        try:
            doc.Delete(l_id)
        except:
            pass
    t_clean.Commit()
    uidoc.RefreshActiveView()

    # TODO: Ensure temporary detail lines are always removed,
    # even if an exception occurs during user confirmation.
    # Consider wrapping the confirmation workflow in try/finally.

    # TODO: Review whether exceptions during temporary line creation
    # should be logged rather than silently ignored.

    return user_selection_is_side_a

# Tolerance configuration for downstream sorting engine
TOL = 0.05
def same(p1, p2):
    return p1.DistanceTo(p2) < TOL

# package_track: For each boundary curve, identify the closest original Wall element and
# package it together with the curve's start and end XYZ points.
def package_track(curves_list, walls):
    packaged = []
    for c in curves_list:
        p_start = c.GetEndPoint(0)
        p_end = c.GetEndPoint(1)
        mid_point = c.Evaluate(0.5, True) # (Normalized = True) returns XYZ object for midpoint

        matched_wall = None # variable to store matched wall that best matches current curve
        closest_dist = float('inf') # Start with infinity so any real distance is smaller.
        for w in walls:
            if isinstance(w.Location, LocationCurve): # if wall's location object is a location curve
                dist = w.Location.Curve.Distance(mid_point) # call distance method on wall's location curve
                if dist < closest_dist: # if dist less than current value of closest_dist
                    closest_dist = dist
                    matched_wall = w
        packaged.append({"Wall": matched_wall, "Start": p_start, "End": p_end})
    return packaged
# NOTE: found is reset to False at the start of each while iteration.
# The for loop then checks EVERY remaining curve looking for a connection.
# If a match is found, found is set to True and the for loop exits early.
# The 'if not found' check is ONLY reached after the for loop finishes.
# If found is True, the check is skipped and the next while iteration begins.
# If found is still False (no match found after checking every remaining curve),
# the while loop is exited.

# Define standard loop sorting function that works regardless of track alignment variations
def sort_packaged_track(raw_edges_list):
    if not raw_edges_list: # checks for empty list - e.g if passed raw_side_b in closed loop scenario, returns empty list & does not try to sort
        return []
    unused = raw_edges_list[:]
    current = unused.pop(0)
    ordered_list = [current]
    current_point = current["End"]

    while unused:
        found = False
        for i, edge in enumerate(unused):
            s = edge["Start"]
            e = edge["End"]
            w = edge["Wall"]
            if same(s, current_point):
                ordered_list.append({"Wall": w, "Start": s, "End": e})
                current_point = e
                unused.pop(i)
                found = True
                break # exits the FOR loop
            elif same(e, current_point):
                ordered_list.append({"Wall": w, "Start": e, "End": s})
                current_point = s
                unused.pop(i)
                found = True
                break # exits the FOR loop
        if not found: # if match found, this evaluates to 'if not true' (i. if FALSE) and while loop continues
            break

    # TODO - Review fallback behaviour below.
    # Currently any unsorted curves are appended to the end of the list.
    # Consider warning the user or stopping the tool instead, as remaining
    # curves may indicate an unexpected geometry or sorting failure.

    # Fallback safety: if there are remaining unsorted segments due to a geometry split, append them safely
    if unused:
        for remaining in unused:
            ordered_list.append(remaining)

    return ordered_list

# def cross_product: Calculates thes Z value of the cross product for 3 points. 

# Returns the signed Z component of the cross product formed by
# three consecutive points (p1 → p2 → p3).
#
# Positive value  = left turn
# Negative value  = right turn
#
# Since the selected exterior track always has OUTSIDE on its LEFT,
# right turns represent external corners and left turns represent
# internal corners.

def cross_product_z(p1, p2, p3):
    v1_x = p2.X - p1.X
    v1_y = p2.Y - p1.Y
    v2_x = p3.X - p2.X
    v2_y = p3.Y - p2.Y
    return (v1_x * v2_y) - (v1_y * v2_x)

def determine_corner_condition(edge_index, is_closed_loop_layout, ordered_data, pt_start, pt_end, num_edges):
    # START CONDITION
    # If this is the first edge in an open run, there is no previous wall segment forming a corner,
    # so the start point is an open end.
    # NOTE: start_is_open and end is open now appear redundant - consider removing
    if edge_index == 0 and not is_closed_loop_layout:
        start_is_external = False 
        start_is_open = True
        print("Start condition : OPEN END")

    # Calculates the turn through the corner where the previous edge meets the start of the current edge.
    else:
        edge_prev = ordered_data[(edge_index - 1) % num_edges]

        # Turn from previous edge into current edge
        cp_start_z = cross_product_z(edge_prev["Start"], edge_prev["End"], pt_end)

        # cp_start_z > 0 means the path turns LEFT.
        # Since outside is on the LEFT, a LEFT turn is INTERNAL.
        if cp_start_z < 0:
            start_is_external = True
        else:
            start_is_external = False

        start_is_open = False

        print("cp_start_z       :", cp_start_z)
        print("start_external   :", start_is_external)

    # END CONDITION
    # If this is the last edge in an open run, there is no following wall segment forming a corner,
    # so the end point is an open end.
    if edge_index == num_edges - 1 and not is_closed_loop_layout:
        end_is_external = False
        end_is_open = True
        print("End condition   : OPEN END")

    # Calculates the turn through the corner where the current edge meets the next edge.
    else:
        edge_next = ordered_data[(edge_index + 1) % num_edges]

        # Turn from current edge into next edge
        cp_end_z = cross_product_z(pt_start, pt_end, edge_next["End"])

        # cp_end_z > 0 means the path turns LEFT.
        # Since outside is on the LEFT, a LEFT turn is INTERNAL.
        if cp_end_z < 0:
            end_is_external = True
        else:
            end_is_external = False

        end_is_open = False

        print("cp_end_z         :", cp_end_z)
        print("end_external     :", end_is_external)

    return start_is_external, end_is_external 

def determine_brick_condition(edge_index, num_edges, is_closed_loop_layout, start_is_external, end_is_external):

    if (edge_index == 0 or edge_index == num_edges - 1) and not is_closed_loop_layout:
        if num_edges == 1: brick_condition = "Co-" 
        elif edge_index == 0: brick_condition = "Co-" if end_is_external else "Co"
        else: brick_condition = "Co-" if start_is_external else "Co"
    else:
        if start_is_external and end_is_external: brick_condition = "Co-"   
        elif (start_is_external and not end_is_external) or (not start_is_external and end_is_external): brick_condition = "Co"    
        else: brick_condition = "Co+"   

    return brick_condition

def classify_brick_conditions(ordered_data, is_closed_loop_layout):

    num_edges = len(ordered_data)
    edges = []

    print("\n===== PART F: CORNER CLASSIFICATION =====")
    print("Closed Loop :", is_closed_loop_layout)
    print("Rule        : OUTSIDE is LEFT of selected exterior track")
    print("Therefore  : RIGHT turn = external corner")


    # Calculate length of curve
    for i in range(num_edges):
        edge_curr = ordered_data[i]
        pt_start = edge_curr["Start"]
        pt_end = edge_curr["End"]

        dx_mm = (pt_end.X - pt_start.X) * 304.8    # convert to mm
        dy_mm = (pt_end.Y - pt_start.Y) * 304.8    # convert to mm
        length_mm = math.sqrt(dx_mm**2 + dy_mm**2) # Calculate the true (Euclidean) length of the edge using the X and Y
                                                    # coordinate differences (Pythagorean theorem). Works for walls at any angle.

        # TODO - Consider storing curve length during package_track().
        # At that point the original Curve object is still available, so c.Length could
        # be converted to mm and stored in the package dictionary, avoiding the need to
        # recalculate length later from Start/End XYZ points.

        start_is_external, end_is_external = determine_corner_condition(i, is_closed_loop_layout, ordered_data, pt_start, pt_end, num_edges)


        wall_info = {
            "Wall Object": edge_curr["Wall"], # Injects physical wall object reference safely into data map
            "Points List": [(pt_start.X * 304.8, pt_start.Y * 304.8, pt_start.Z * 304.8), 
                            (pt_end.X * 304.8, pt_end.Y * 304.8, pt_end.Z * 304.8)],
            "Length": length_mm,
            "Condition": determine_brick_condition(i, num_edges, is_closed_loop_layout, start_is_external, end_is_external)   
        }
        edges.append(wall_info)

    return edges

def resize(length, condition):
    if condition == "Co-": grid_length = length + 10
    elif condition == "Co+": grid_length = length - 10
    else: grid_length = length

    half_brick_units = round(grid_length / 112.5) 

    if condition == "Co-": return (half_brick_units * 112.5 - 10)
    elif condition == "Co+": return (half_brick_units * 112.5 + 10)
    else: return (half_brick_units * 112.5)

def calculate_target_centreline(edge_data):
    wall = edge_data["Wall Object"]
    wall_loc = wall.Location

    if not isinstance(wall_loc, LocationCurve):
        raise ValueError("Wall does not have a LocationCurve.")

    start_mm = edge_data["Points List"][0]
    end_mm = edge_data["Points List"][1]

    # Convert resized edge coordinates from millimetres to feet.
    pt_start_track = XYZ(start_mm[0] / 304.8, start_mm[1] / 304.8, start_mm[2] / 304.8)
    pt_end_track = XYZ(end_mm[0] / 304.8, end_mm[1] / 304.8, end_mm[2] / 304.8)

    # Calculate the edge direction and its perpendicular vector.
    track_dir = (pt_end_track - pt_start_track).Normalize() 
    perpend_vector = XYZ(-track_dir.Y, track_dir.X, 0.0)

    half_thickness_feet = wall.WallType.Width / 2.0

    # Create test points on either side of the resized edge.
    # Determine which side of the edge the original wall centreline lies on.
    test_pt_positive = pt_start_track + (perpend_vector * half_thickness_feet)
    test_pt_negative = pt_start_track - (perpend_vector * half_thickness_feet)

    dist_pos = wall_loc.Curve.Distance(test_pt_positive)
    dist_neg = wall_loc.Curve.Distance(test_pt_negative)

    # Shift the resized edge by half the wall thickness to create the new centreline.
    if dist_pos < dist_neg:
        correct_shift_vector = perpend_vector * half_thickness_feet

    else:
        correct_shift_vector = (-perpend_vector) * half_thickness_feet

    pt_start_center = pt_start_track + correct_shift_vector
    pt_end_center = pt_end_track + correct_shift_vector 

    new_line = Line.CreateBound(pt_start_center, pt_end_center)

    return new_line 

def apply_centreline_to_wall(wall, new_line):
    wall_loc = wall.Location
    loc_param = wall.get_Parameter(BuiltInParameter.WALL_KEY_REF_PARAM)

    if loc_param and not loc_param.IsReadOnly:
        loc_param.Set(0)

    # Retrieve the wall's built-in "Location Line" parameter.
    # get_Parameter() returns a Parameter object, allowing us to read or
    # modify the parameter value. WALL_KEY_REF_PARAM is the enum value that
    # identifies the Location Line parameter.

    # TODO - Review error handling.
    # This currently skips the update if the parameter is missing or read-only.
    # Since this tool only operates on Wall objects, consider whether it would
    # be better to raise an error instead.


    if wall.Flipped:
        wall.Flip()

    wall_loc.Curve = new_line


# ==============================================================================
# A. SETUP AND VALIDATION
# ==============================================================================
selection = revit.get_selection()
selected_elements = list(selection)
walls = [el for el in selected_elements if isinstance(el, Wall)] # if instance is a wall, append to walls list

if not walls:
    UI.TaskDialog.Show(
        "Brick Layout",
        "No walls are currently selected. Select your walls first, then run the tool again."
    )
    script.exit()
    
print("[Brick Coordinator] Running wall-processing engine.")

# ADD PRINT DIAGNOSTIC TO DETERMINE SEQUENCE OF SELECTED WALL ELEMENTS (START AND END POINTS) 
print("\n===== ORIGINAL REVIT WALLS =====")

for i, wall in enumerate(walls):

    curve = wall.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)

    print("\nWall {}".format(i))
    print("Element ID :", wall.Id)
    print("Flipped    :", wall.Flipped)
    print("Start      : ({:.1f}, {:.1f})".format(start.X * 304.8, start.Y * 304.8))
    print("End        : ({:.1f}, {:.1f})".format(end.X * 304.8, end.Y * 304.8))


doc = revit.doc
uidoc = revit.uidoc

# ==============================================================================
# B. GEOMETRY EXTRACTION: UNIFIED SOLID UNION EXTRACTION & BOUNDARY SEPARATION
# ==============================================================================

all_loops, wall_thickness_feet = extract_wall_boundary_loops(walls)

# ==============================================================================
# C. SHAPE DETECTION
# ==============================================================================

# Interpret the extracted wall boundary loops as either an open wall run or a closed wall layout, and return the two wall-side curve collections.

lines_side_a, lines_side_b, is_closed_loop_layout = shape_detection_and_track_separation(
    all_loops,
    wall_thickness_feet
)

# ==============================================================================
# D. USER CONFIRMATION
# ==============================================================================
# At this point:

# lines_side_a contains one side of the wall run.
# lines_side_b contains the opposite side of the wall run.

# The script must now determine which side represents the exterior face.

# Visual highlighting using temporary View Detail Lines.
# The highlighted Side A is shown to the user, who confirms
# whether it represents the exterior face.

user_selection_is_side_a = confirm_exterior_track(lines_side_a, doc, uidoc)
    
# PRINT DIAGNOSTIC
print("\n===== USER CONFIRMATION =====")
print("User selected Side A:", user_selection_is_side_a)

# ==============================================================================
# E. SORTING
# =================================================================================

# At this point:
#
# lines_side_a and lines_side_b contain the two possible wall face tracks.
# This is true for both open wall runs and closed loop layouts.
#
# user_selection_is_side_a stores the user's confirmation from Part D:
# True  = use Side A as the exterior face
# False = use Side B as the exterior face
#
# Part E now packages and sorts only the user-selected side.

# --------------------------
# NOTE: FUTURE ARCHITECTURE REVIEW
# --------------------------
# Part D currently returns the boolean:
#     user_selection_is_side_a
#
# Part E then resolves this into the selected exterior track.
#
# Consider simplifying the data flow by introducing:
#     selected_track
#
# or by having Part D return the selected track directly, allowing
# downstream Parts E–H to operate on the resolved exterior track without
# needing knowledge of Side A and Side B.
#
# Review after the function-extraction refactor is complete.


if user_selection_is_side_a:
    raw_side = package_track(lines_side_a, walls)
else:
    raw_side = package_track(lines_side_b, walls)


# Sort selected track cleanly
ordered_data = sort_packaged_track(raw_side)


# # PRINT DIAGNOSTIC
# print("\n===== SORTED TRACK =====")

# for i, edge in enumerate(ordered_data):

#     wall = edge["Wall"]
#     start = edge["Start"]
#     end = edge["End"]

#     print("\nEdge {}".format(i))
#     print("Element ID :", wall.Id)
#     print("Flipped    :", wall.Flipped)
#     print("Start      : ({:.1f}, {:.1f})".format(start.X * 304.8, start.Y * 304.8))
#     print("End        : ({:.1f}, {:.1f})".format(end.X * 304.8, end.Y * 304.8))


# PRINT DIAGNOSTIC
# print("\n===== OUTSIDE SIDE TEST =====")

# print("User selected Side A :", user_selection_is_side_a)
# print("Testing selected exterior track only")

# half_thickness_feet = wall_thickness_feet / 2.0

# for i, edge in enumerate(ordered_data):
#     wall = edge["Wall"]
#     start = edge["Start"]
#     end = edge["End"]

#     track_dir = (end - start).Normalize()
#     left_vec = XYZ(-track_dir.Y, track_dir.X, 0.0)
#     right_vec = -left_vec

#     mid = XYZ(
#         (start.X + end.X) / 2.0,
#         (start.Y + end.Y) / 2.0,
#         (start.Z + end.Z) / 2.0
#     )

#     test_left = mid + (left_vec * half_thickness_feet)
#     test_right = mid + (right_vec * half_thickness_feet)

#     dist_left = wall.Location.Curve.Distance(test_left)
#     dist_right = wall.Location.Curve.Distance(test_right)

#     print("\nEdge {}".format(i))
#     print("Wall flipped :", wall.Flipped)
#     print("Left test distance to wall centreline  : {:.4f}".format(dist_left))
#     print("Right test distance to wall centreline : {:.4f}".format(dist_right))

#     if dist_left < dist_right:
#         print("Wall core is on LEFT of selected track")
#         print("Therefore OUTSIDE is on RIGHT")
#     else:
#         print("Wall core is on RIGHT of selected track")
#         print("Therefore OUTSIDE is on LEFT")
# ==============================================================================
# F. AUTOMATIC VECTOR CORNER ANALYSIS & BRICK CONDITION ASSIGNMENT
# =================================================================================

# At this point:
#
# 'ordered_data' contains a sequentially ordered list of dictionaries.
# Each dictionary stores the matched Wall element plus the Start and End XYZ points.

EDGES = classify_brick_conditions(ordered_data, is_closed_loop_layout)

# ==============================================================================
# G. RESIZE LENGTH 
# ==============================================================================

# At this point:
#
# EDGES Dictionary contains: wall object, points list, length and condition for each wall segment

EDGES_copy = []
for edge in EDGES:
    EDGES_copy.append({
        "Wall Object": edge["Wall Object"],
        "Points List": list(edge["Points List"]), # (x, y, z), (x, y, z)
        "Length": edge["Length"],
        "Condition": edge["Condition"]
    })


for i in range(len(EDGES_copy)):

    if i == 0:
        current_start = EDGES[i]["Points List"][0]
    else:
        current_start = prev_end_pt

    # TODO: Investigate whether intermittant for irregular shaped loops where one join is failing could 
    # be rectified by dealing with last edge in list separately if a closed loop (make end point same as start point)

    EDGES_copy[i]["Length"] = resize(EDGES[i]["Length"], EDGES[i]["Condition"])

    new_length = EDGES_copy[i]["Length"] 

    orig_start = EDGES[i]["Points List"][0]
    orig_end = EDGES[i]["Points List"][1]

    dx = orig_end[0] - orig_start[0]
    dy = orig_end[1] - orig_start[1]

    if abs(dx) > abs(dy): # EDGE IS HORIZONTAL
        direction = 1.0 if dx > 0.0 else -1.0
        new_end = (current_start[0] + (new_length * direction), current_start[1], current_start[2])

    else: # EDGE IS VERTICAL
        direction = 1.0 if dy > 0.0 else -1.0
        new_end = (current_start[0], current_start[1] + (new_length * direction), current_start[2])

    EDGES_copy[i]["Points List"][0] = current_start
    EDGES_copy[i]["Points List"][1] = new_end
    prev_end_pt = new_end


# ==============================================================================
# FINAL PRINT REPORT
# ==============================================================================
print("\n--- BRICK COORDINATOR PROCESSED OUTPUT ---")
for idx in range(len(EDGES)):
    print("Wall Segment [{}]:".format(idx))
    print("  -> Original Length : {:.1f}mm".format(EDGES[idx]["Length"]))
    print("  -> Corner Condition: {}".format(EDGES[idx]["Condition"]))
    print("  -> Target Brick Dim: {:.1f}mm".format(EDGES_copy[idx]["Length"]))

# :.1f is a format specifier:
# :    = formatting instructions follow
# .1   = display 1 decimal place
# f    = format as a floating-point number

# ==============================================================================
# H: AUTOMATIC PHYSICAL MODEL REPOSITIONING 
# ==============================================================================

# At this point EDGES_copy contains the processed data for each wall:
# - reference to the original Revit Wall element
# - recalculated brick-coordinated length
# - updated start and end coordinates
# - corner condition.


t_move = Transaction(doc, "Reposition and Co-ordinate Walls")
t_move.Start()

try:
    # Temporarily disallow joins on all selected walls to prevent Revit panics
    for edge_data in EDGES_copy:
        wall = edge_data["Wall Object"] # create new reference (not a new wall object!) to wall object from the reference in edge_data
        if wall is not None: 
            WallUtils.DisallowWallJoinAtEnd(wall, 0)
            WallUtils.DisallowWallJoinAtEnd(wall, 1)
            

    for edge_data in EDGES_copy:
        wall = edge_data["Wall Object"]
        new_line = calculate_target_centreline(edge_data)
        apply_centreline_to_wall(wall, new_line)

       
    for edge_data in EDGES_copy:
        wall = edge_data["Wall Object"]
        if wall is not None:
            WallUtils.AllowWallJoinAtEnd(wall, 0)
            WallUtils.AllowWallJoinAtEnd(wall, 1)

    t_move.Commit()
    print("\n[SUCCESS]: Physical walls have been automatically adjusted and aligned to brick dimensions.")
    uidoc.RefreshActiveView()
    

except Exception as e:
    t_move.RollBack() # return to state before try block
    UI.TaskDialog.Show("Execution Error", "Failed to reposition structural walls: {}".format(str(e)))


    
   
            
   
   
      



