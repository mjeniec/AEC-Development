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
# A. ROUTER: decide which known-good engine to run
# ==============================================================================
selection = revit.get_selection()
selected_elements = list(selection)
walls = [el for el in selected_elements if isinstance(el, Wall)] # if instance is a wall, append to walls list

# if walls is empty - script exits
if not walls:
    UI.TaskDialog.Show("Brick Layout", "No walls are currently selected. Select your walls first, then run the tool again.")
    script.exit()

flipped_count = 0
for w in walls:
    if w.Flipped:
        flipped_count += 1

# If one or more selected walls are flipped, run the real flipped-wall engine.
# Otherwise, run the original non-flipped-wall engine.
# Note: the flipped-wall engine intentionally contains its own wall.Flip() / wall_loc.Curve sequence.

if flipped_count > 0:
    print("[Brick Coordinator Router] Detected {0} flipped wall(s). Running REAL flipped-wall source script.".format(flipped_count))

# ==========================================================================
# FLIPPED-WALL ENGINE
# ==========================================================================
    doc = revit.doc
    uidoc = revit.uidoc
    selection = revit.get_selection()

# ==============================================================================
# B. GEOMETRY EXTRACTION: UNIFIED SOLID UNION EXTRACTION & BOUNDARY SEPARATION
# ==============================================================================
    UI.TaskDialog.Show("Brick Layout", "Select your walls, then click Finish on the Options Bar.")

    selected_elements = list(selection)
    walls = [el for el in selected_elements if isinstance(el, Wall)]

    if not walls:
        UI.TaskDialog.Show("Error", "No valid Walls were selected. Execution aborted.")
        script.exit()

    # Extracted thickness from the first wall instance safely
    wall_thickness_feet = walls[0].WallType.Width

    # 1. Fuse ALL wall solids to dissolve butt joints and calculate corners
    geo_options = Options() # Creates a Revit geometry settings object.
    geo_options.ComputeReferences = False
    geo_options.DetailLevel = ViewDetailLevel.Fine # Give me most detailed (FIne) version of geometry
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

    # Tolerance configuration for downstream sorting engine
    tol = 0.05
    def same(p1, p2):
        return p1.DistanceTo(p2) < tol

# ==============================================================================
# C. SHAPE DETECTION
# ==============================================================================

    # At this point: we have a list of all the curveloops extracted from bottom face of fused solid.

    # If all_loops contains only one CurveLoop, store that loop in selected_loop.
    # Otherwise, take all the CurveLoop objects in all_loops, use GetExactLength() to calculate the 
    # perimeter of each loop, and store the loop with the greatest perimeter in selected_loop. 
    # NOTE: Future introduction of user check for closed loop walls - take multiple curve loops forward as selected loop. 
   
    selected_loop = all_loops[0] if len(all_loops) == 1 else max(all_loops, key=lambda l: l.GetExactLength())

    # Convert the CurveLoop container into an iterable list of individual Curve objects
    loop_curves = [c for c in selected_loop] # list of curves
    num_curves = len(loop_curves) # number of curves

    # Find the indices of the end-caps matching the wall thickness
    cap_indices = []
    for idx, curve in enumerate(loop_curves):
        if abs(curve.Length - wall_thickness_feet) < 0.083: # 1-inch variance tolerance
            cap_indices.append(idx)

    # Create side lists before determining if wall layout is open or closed
    lines_side_a = []
    lines_side_b = []

    # PART 2 - At this point: 
    # We have converted the selected CurveLoop into a Python list of
    # individual Curve objects (loop_curves), ready to analyse.

    # If all_loops contains more than one loop or we don't find exactly two end caps, it's a closed structural loop layout
    if len(all_loops) > 1 or len(cap_indices) != 2:
        is_closed_loop_layout = True
        print("Morphology Identified: Closed Loop. Isolating exterior perimeter by area scaling.")
        outer_loop = max(all_loops, key=lambda l: l.GetExactLength()) # NOTE: MAY DELETE AS REPEATED FROM PART 1
        lines_side_a = [curve for curve in outer_loop] # NOTE: REPLACE WITH lines_side_a = loop_curves SEE PART 1
    # NOTE: if add user confirmation for closed loop, assign one curve from all_loops into lines_side_a and one into lines_side_b
  
    else:
        is_closed_loop_layout = False
        print("Morphology Identified: Open String. Splitting parallel tracks topologically...")

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

        if not lines_side_a or not lines_side_b:
            UI.TaskDialog.Show("Geometry Error", "Could not split the profile loop into distinct tracks.")
            script.exit()

# ==============================================================================
# D. USER CONFIRMATION
# ==============================================================================
    # At this point:

    # Closed loop layout: lines_side_a contains the curve segments of the selected perimeter loop
    # (currently assumed to be the exterior loop). NOTE: Future user check to be added to deal with
    # internal courtyard edge case. 

    # Open wall run:
    # lines_side_a contains one side of the wall run.
    # lines_side_b contains the opposite side of the wall run.

    # The script must now determine which side represents the exterior face.

    # Visual highlighting using View Detail Lines (Only applies to Open Strings)
    

    if not is_closed_loop_layout: 
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

    
    else: 
        user_selection_is_side_a = True

# TODO - Future improvement:take both lines forward (a and b) for both closed and open loop scenario. 
# Ask user to confirm side. Take chosen side into sorting.

# ==============================================================================
# E. SORTING
# =================================================================================
  
# At this point:
#
# Closed loop layout:
# lines_side_a contains the curve segments forming the outer perimeter of the
# wall layout. In the current flipped-wall engine this is assumed to be the
# exterior boundary, so flipped closed-loop layouts are not yet coordinated
# correctly.
#
# TODO - Future improvement:
# Introduce the same user confirmation used for open wall runs, allowing the
# user to confirm which perimeter is the true exterior boundary (e.g. courtyard
# layouts) so both flipped and unflipped closed loops are handled correctly.

# Open wall run:
# lines_side_a and lines_side_b contain the two long sides of the wall run.
# user_selection_is_side_a identifies which side the user confirmed as the
# exterior face.



# For each boundary curve, identify the closest original Wall element and
# package it together with the curve's start and end XYZ points.
    
    def package_track(curves_list):
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


# TODO - Review whether both tracks need packaging/sorting.
# The correct track is already known, so only the selected side may need processing.
    raw_side_a = package_track(lines_side_a)
    raw_side_b = package_track(lines_side_b) if not is_closed_loop_layout else []



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

    # Sort both tracks cleanly
    sorted_side_a = sort_packaged_track(raw_side_a)
    sorted_side_b = sort_packaged_track(raw_side_b)

    # Select the winner based on user choice
    if user_selection_is_side_a or is_closed_loop_layout:
        ordered_data = sorted_side_a
    else:
        ordered_data = sorted_side_b

    # Extract the sorted endpoints required downstream for calculation matrices
    ordered = [(item["Start"], item["End"]) for item in ordered_data]

# ==============================================================================
# F. AUTOMATIC VECTOR CORNER ANALYSIS & BRICK CONDITION ASSIGNMENT
# =================================================================================
  
# At this point:
#
# 'ordered_data' contains a sequentially ordered list of dictionaries.
# Each dictionary stores the matched Wall element plus the Start and End XYZ points.
#
# 'ordered' contains the same sequence stripped down to Start/End XYZ pairs only.

    num_edges = len(ordered)
    EDGES = []

    first_point = ordered[0][0]
    last_point = ordered[-1][1]
    is_closed_loop_layout = same(first_point, last_point) 

# TODO - Review whether this closed-loop check is still required.
# The layout type was already determined in Section C and has not changed.
# Consider reusing the existing is_closed_loop_layout value.


# def cross_product: Calculates thes Z value of the cross product for 3 points. 
# Returns a positive or negative value describing the turn direction
# between three consecutive points (p1 -> p2 -> p3).
#
# The sign (positive or negative) is later used to determine the overall
# loop direction (clockwise or counter-clockwise) and identify
# internal/external corners.

    def cross_product_z(p1, p2, p3):
        v1_x = p2.X - p1.X
        v1_y = p2.Y - p1.Y
        v2_x = p3.X - p2.X
        v2_y = p3.Y - p2.Y
        return (v1_x * v2_y) - (v1_y * v2_x)

    user_direction_override = False 

# Calculate whether diection is cw of ccw
    if is_closed_loop_layout:
        total_turn_sign = 0 
        for i in range(num_edges):
            edge_curr = ordered[i]
            edge_next = ordered[(i + 1) % num_edges] 
            # Use the modulo (%) operator to wrap from the last edge back to the first,
            # allowing the final corner of a closed loop to be analysed.
            cp_z = cross_product_z(edge_curr[0], edge_curr[1], edge_next[1]) 
            if cp_z > 0: total_turn_sign += 1
            elif cp_z < 0: total_turn_sign -= 1
        is_ccw = total_turn_sign > 0 
    else:
        is_ccw = user_direction_override # NOTE check this as default should cause mistakes but doesn't

    # DEBUG POINT 1
    print("\n===== DIRECTION =====")
    print("Closed Loop :", is_closed_loop_layout)
    print("is_ccw      :", is_ccw)


# Calculate length of curve
    for i in range(num_edges):
        edge_curr = ordered[i]
        pt_start = edge_curr[0]
        pt_end = edge_curr[1]

        # DEBUG POINT 2
        print("\n----------------------------")
        print("Edge", i)
        print("Start :", pt_start)
        print("End   :", pt_end)

        dx_mm = (pt_end.X - pt_start.X) * 304.8    # convert to mm
        dy_mm = (pt_end.Y - pt_start.Y) * 304.8    # convert to mm
        length_mm = math.sqrt(dx_mm**2 + dy_mm**2) # Calculate the true (Euclidean) length of the edge using the X and Y
                                                   # coordinate differences (Pythagorean theorem). Works for walls at any angle.

# TODO - Consider storing curve length during package_track().
# At that point the original Curve object is still available, so c.Length could
# be converted to mm and stored in the package dictionary, avoiding the need to
# recalculate length later from Start/End XYZ points.

# below block calculates end condition of each curve using cross product z and direction

        # If this is the first edge in an open run, there is no previous wall segment forming a corner,
        # so the start point is an open end.
        if i == 0 and not is_closed_loop_layout:
            start_is_external = False 
            start_is_open = True

        # Calculates the turn through the corner where the previous edge meets the start of the current edge.
        else:
            edge_prev = ordered[(i - 1) % num_edges] 
            cp_start_z = cross_product_z(edge_prev[0], edge_prev[1], pt_end) # this could be (edge_prev[0], pt_start, pt_end) - dosn't matter
            
            if is_ccw:

                if cp_start_z > 0:
                    start_is_external = True
                else:
                    start_is_external = False

            else: # (is cw)

                if cp_start_z < 0:
                    start_is_external = True
                else:
                    start_is_external = False
            
            # DEBUG POINT 3
            print("cp_start_z       :", cp_start_z)
            print("start_external   :", start_is_external)

            start_is_open = False

      
        # If this is the last edge in an open run, there is no following wall segment forming a corner,
        # so the end point is an open end.
        if i == num_edges - 1 and not is_closed_loop_layout:
            end_is_external = False
            end_is_open = True

       # Calculates the turn through the corner where the current edge meets the next edge.
        else:
            edge_next = ordered[(i + 1) % num_edges]
            cp_end_z = cross_product_z(pt_start, pt_end, edge_next[1])
            end_is_external = cp_end_z > 0 if is_ccw else cp_end_z < 0
            end_is_open = False

        
        if (i == 0 or i == num_edges - 1) and not is_closed_loop_layout:
            if num_edges == 1: brick_condition = "Co-" 
            elif i == 0: brick_condition = "Co-" if end_is_external else "Co"
            else: brick_condition = "Co-" if start_is_external else "Co"
        else:
            if start_is_external and end_is_external: brick_condition = "Co-"   
            elif (start_is_external and not end_is_external) or (not start_is_external and end_is_external): brick_condition = "Co"    
            else: brick_condition = "Co+"   

        wall_info = {
            "Wall Object": ordered_data[i]["Wall"], # Injects physical wall object reference safely into data map
            "Points List": [(pt_start.X * 304.8, pt_start.Y * 304.8, pt_start.Z * 304.8), 
                            (pt_end.X * 304.8, pt_end.Y * 304.8, pt_end.Z * 304.8)],
            "Length": length_mm,
            "Condition": brick_condition
        }
        EDGES.append(wall_info)

# ==============================================================================
# G. RESIZE LENGTH 
# ==============================================================================

# At this point:
#
# EDGES Dictionary contains: wall object, points list, length and condition for each wall segment
 
    
    def resize(length, condition):
        if condition == "Co-": grid_length = length + 10
        elif condition == "Co+": grid_length = length - 10
        else: grid_length = length

        half_brick_units = round(grid_length / 112.5) 

        if condition == "Co-": return (half_brick_units * 112.5 - 10)
        if condition == "Co+": return (half_brick_units * 112.5 + 10)
        if condition == "Co": return (half_brick_units * 112.5)

    # Create a safe copy of the EDGES matrix without attempting to deepcopy Revit API Wall elements (doesn't work!)
    # Create a second copy of the edge data.
    #
    # We do NOT use deepcopy() because the Revit Wall objects cannot safely be deep copied.
    # We only need a new copy of the data that will be modified
    # (points, lengths, conditions), while keeping references
    # to the original Revit Wall objects.
    #
    # Learn more about Python references later.
    
    
    EDGES_copy = []
    for edge in EDGES:
        EDGES_copy.append({
            "Wall Object": edge["Wall Object"],
            "Points List": list(edge["Points List"]), # (x, y, z), (x, y, z)
            "Length": edge["Length"],
            "Condition": edge["Condition"]
        })

    # Resize leading segment (Segment 0)
    EDGES_copy[0]["Length"] = resize(EDGES[0]["Length"], EDGES[0]["Condition"])
    start_pt = EDGES_copy[0]["Points List"][0] # (x, y, z)
    end_pt = EDGES[0]["Points List"][1] # (x, y, z)
    dx = end_pt[0] - start_pt[0] # x end - x start
    dy = end_pt[1] - start_pt[1] # y end - y start
    # dx and dy describe the original edge's direction vector.
    # Their magnitude gives the distance travelled along each axis.
    # Their sign (+/-) gives the direction of travel.

    if abs(dx) > abs(dy): # Edge is horizontal (X direction)
        direction = 1.0 if dx > 0 else -1.0 # check if direction is positive or negative and store 
        new_end_x = start_pt[0] + (EDGES_copy[0]["Length"] * direction) # calculate new end point x coordinate using resized length
        EDGES_copy[0]["Points List"][1] = (new_end_x, start_pt[1], start_pt[2]) # update only the x coordinate of the end point (rebuild using start point coordinates as safer!)
    
    else: # edge is vertical (Y direction)
        direction = 1.0 if dy > 0 else -1.0 # check if direction is positive or negative and store 
        new_end_y = start_pt[1] + (EDGES_copy[0]["Length"] * direction) # calculate new end point y coordinate using resized length
        EDGES_copy[0]["Points List"][1] = (start_pt[0], new_end_y, start_pt[2]) # update only the y coordinate of the end point (rebuild using start point coordinates as safer!)

    prev_end_pt = EDGES_copy[0]["Points List"][1] # (x, y, z)

    
    for i in range(1, len(EDGES_copy)): # loop through remaining edges 
        EDGES_copy[i]["Points List"][0] = prev_end_pt # update the current edge's start point with previous edge's end point
        EDGES_copy[i]["Length"] = resize(EDGES[i]["Length"], EDGES[i]["Condition"]) # use the original edge's length and condition to calculate the resized length, then store it in EDGES_copy.

        # TODO REMOVE NOTE - NO LONGER RELEVANT?- CRITICAL FIX: Read the delta vectors directly from the freshly chain-linked coordinates 
        # instead of the original raw layout array to protect against flipped normal flows.
        current_start = EDGES_copy[i]["Points List"][0] # (x, y, z) point has been updated to match previous end point
        orig_end = EDGES[i]["Points List"][1] # (x, y, z) take from EDGES (not edges copy) as we want original direction vector (we moved the current start point to match previous end point)
        orig_start = EDGES[i]["Points List"][0] # (x, y, z) take from EDGES (not edges copy) as we want original direction vector (we moved the current start point to match previous end point)

        dx = orig_end[0] - orig_start[0] # x end - x start
        dy = orig_end[1] - orig_start[1] # y end - y start

        if abs(dx) > abs(dy): # Edge is horizontal (X direction)
            direction = 1.0 if dx > 0 else -1.0 # check if direction is positive or negative and store 
            new_end_x = current_start[0] + (EDGES_copy[i]["Length"] * direction) # calculate new end point x coordinate using resized length
            EDGES_copy[i]["Points List"][1] = (new_end_x, current_start[1], current_start[2]) # update only the x coordinate of the end point (rebuild using start point coordinates as safer!)
        
        else: # Edge is horizontal (Y direction)
            direction = 1.0 if dy > 0 else -1.0 # check if direction is positive or negative and store 
            new_end_y = current_start[1] + (EDGES_copy[i]["Length"] * direction) # calculate new end point y coordinate using resized length
            EDGES_copy[i]["Points List"][1] = (current_start[0], new_end_y, current_start[2]) # update only the y coordinate of the end point (rebuild using start point coordinates as safer!)

        prev_end_pt = EDGES_copy[i]["Points List"][1] # update prev_end_point with current end point. 


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
    # H: AUTOMATIC PHYSICAL MODEL REPOSITIONING (FLIP-AWARE ENGINE)
    # ==============================================================================

    # At this point:
    #
    # EDGES_copy contains the processed edge data for each wall:
    # - a reference to the original Revit Wall element,
    # - recalculated brick-coordinated length,
    # - updated start and end coordinates,
    # - and the corner condition.
    #
    # This information will now be used to physically reposition the walls in Revit.


    # Open a database transaction to push changes into the active Revit document
    t_move = Transaction(doc, "Reposition and Co-ordinate Walls")
    t_move.Start()

    try:
        # STEP 1: Temporarily disallow joins on all selected walls to prevent Revit panics
        for edge_data in EDGES_copy:
            wall = edge_data["Wall Object"] # create new reference (not a new wall object!) to wall object from the reference in edge_data
            if wall is not None: 
                WallUtils.DisallowWallJoinAtEnd(wall, 0)
                WallUtils.DisallowWallJoinAtEnd(wall, 1)
                # Temporarily set both wall ends to "Do Not Join" so Revit
                # doesn't automatically modify wall geometry while we reposition it


        # STEP 2: Shift, resize, and position every wall using dynamic alignment
        for edge_data in EDGES_copy:
            wall = edge_data["Wall Object"]
            if wall is None: # probably not really needed
                continue


            # Use the Wall reference to retrieve the wall's Location property.
            # For walls, this is normally a LocationCurve object.
            wall_loc = wall.Location           
            # Check that the Location object is actually a LocationCurve
            # before using LocationCurve-specific properties and methods.
            if isinstance(wall_loc, LocationCurve):
                # 1. Pull the cleanly calculated target track footprint coordinates from Phase 5
                start_mm = edge_data["Points List"][0]
                end_mm = edge_data["Points List"][1]

                # 2. Convert target track footprint points into feet
                # Divide each coordinate by 304.8 to convert mm → feet.
                # Pass the converted X, Y and Z values into the XYZ class to create Revit XYZ point objects.
                pt_start_track = XYZ(start_mm[0] / 304.8, start_mm[1] / 304.8, start_mm[2] / 304.8)
                pt_end_track = XYZ(end_mm[0] / 304.8, end_mm[1] / 304.8, end_mm[2] / 304.8)

                # 3. Calculate a clean, 2D perpendicular vector from the target line path
                # Create a vector pointing from the start point to the end point.
                # A vector describes a direction and a distance, not a position.
                #
                # Normalize() keeps the direction the same but changes the vector's
                # length to exactly 1 (a unit vector). This removes the original wall
                # length so we can later multiply the vector by any distance we want
                # (e.g. half the wall thickness).
                track_dir = (pt_end_track - pt_start_track).Normalize() 
                
                # Take the wall/edge direction vector and rotate it 90 degrees in plan to create a perpendicular direction vector.
                # This points across the wall, not along it, so it can be used to offset from the external face track to the wall centreline.
                perpend_vector = XYZ(-track_dir.Y, track_dir.X, 0.0) # alternatively could be: XYZ(track_dir.Y, -track_dir.X, 0.0)

                # 4. Calculate exactly half the wall thickness to shift from the face to the centerline
                half_thickness_feet = wall.WallType.Width / 2.0

                # 5. DYNAMIC TARGET CHECK: Test which direction points toward the physical wall core

                # The recalculated brick track represents the EXTERNAL FACE of the wall.
                # The Revit LocationCurve lies at the WALL CENTRELINE.
                # Therefore we must move sideways by half the wall thickness to calculate
                # the new centreline position that the LocationCurve should be moved to.
                #
                # The perpendicular vector tells us the sideways direction, but at this stage we don't know which side points towards the wall core.
                #
                # Because perpend_vector is a NORMALIZED vector (length = 1), multiplyingit by half_thickness_feet produces 
                # a perpendicular offset vector whose length is exactly half the wall thickness.
                #
                # We therefore create two possible centreline positions:
                #   +perpend_vector * half_thickness_feet
                #   -perpend_vector * half_thickness_feet
                #
                # One of these points lies inside the wall (correct centreline direction), while the other lies outside the wall. 
                # The next step measures which test point is closest to the wall's existing LocationCurve, allowing the correct offset direction to be chosen automatically.
                
                test_pt_positive = pt_start_track + (perpend_vector * half_thickness_feet) # stores a point coordinate positioned half the wall thickness away from the recalculated external face point.
                test_pt_negative = pt_start_track - (perpend_vector * half_thickness_feet) # stores a point coordinate positioned half the wall thickness away from the recalculated external face point (on opposite side).

                # Measure distances from both test options to the wall's current original centerline axis.
                # Distance() method automatically gives shortest distances between two objects.
                dist_pos = wall_loc.Curve.Distance(test_pt_positive) 
                dist_neg = wall_loc.Curve.Distance(test_pt_negative)

                # Choose the vector direction that shifts inward towards the wall core.
                if dist_pos < dist_neg:
                    correct_shift_vector = perpend_vector * half_thickness_feet
                else:
                    correct_shift_vector = (-perpend_vector) * half_thickness_feet

                # NOTE : VECTOR MATHMATICS:
                # vector      = same length, original direction
                # -vector     = same length, opposite direction

                # vector * d  = length = d, original direction
                # -vector * d = length = d, opposite direction

                # We now have an offset vector (correct_shift_vector), with length equal to half the wall thickness, pointing from the 
                # recalculated external face track toward the side where the wall centreline should be positioned.

                # 6. Apply the verified vector to find the perfect structural centerline
                pt_start_center = pt_start_track + correct_shift_vector
                pt_end_center = pt_end_track + correct_shift_vector

                # 7. Build the new bounded line geometry along the calculated centerline axis
                new_line = Line.CreateBound(pt_start_center, pt_end_center)

                # 8. Force the Wall location parameter reference to Wall Centerline (Value 0)
                loc_param = wall.get_Parameter(BuiltInParameter.WALL_KEY_REF_PARAM)
                if loc_param and not loc_param.IsReadOnly:
                    loc_param.Set(0)

                # We call the get_Parameter() instance method on our Wall object. 
                # We pass it the BuiltInParameter.WALL_KEY_REF_PARAM enum value, which identifies the built-in parameter that stores the wall's Location Line setting. 
                # BuiltInParameter is the enum type. WALL_KEY_REF_PARAM is one value from that enum.
                # The method returns a Parameter object representing that parameter, which we store in loc_param.

                # TODO - REVIEW ERROR HANDLING.
                #
                # This currently skips the parameter update if the parameter cannot be
                # retrieved or is read-only.
                #
                # Since this tool only operates on Wall objects, investigate whether it
                # would be better to fail immediately with a clear error message rather
                # than silently continuing with a potentially incorrect wall state.



                # 9. CRITICAL FIX: If the wall was manually flipped by the user, 
                # un-flip it before setting the curve to lock the external brick to the outside face.
                # TODO - REVIEW WHETHER THIS IS STILL REQUIRED.
                #
                # This currently un-flips any wall that was manually flipped before the
                # new LocationCurve is assigned.
                #
                # Open wall runs currently produce the correct result, but flipped closed-loop
                # layouts end up with the wrong wall orientation.
                #
                # After implementing user confirmation of the exterior side for closed loops,
                # test whether this wall.Flip() call is still necessary or whether it should
                # be removed or replaced with logic that preserves the user's original flip state.

                if wall.Flipped:
                    wall.Flip()

                # 10. Overwrite the location line curve property to snap the wall cleanly into position
                wall_loc.Curve = new_line

        # STEP 3: Re-allow joins so Revit cleanly calculates the new perfect corners all at once
        for edge_data in EDGES_copy:
            wall = edge_data["Wall Object"]
            if wall is not None:
                WallUtils.AllowWallJoinAtEnd(wall, 0)
                WallUtils.AllowWallJoinAtEnd(wall, 1)

        t_move.Commit()
        print("\n[SUCCESS]: Physical walls have been automatically adjusted and aligned to brick dimensions.")
        uidoc.RefreshActiveView()

    except Exception as e:
        t_move.RollBack()
        UI.TaskDialog.Show("Execution Error", "Failed to reposition structural walls: {}".format(str(e)))

else:
    print("[Brick Coordinator Router] Detected no flipped walls. Running non-flipped source script.")

    # ==========================================================================
    # NON-FLIPPED-WALL ENGINE
    # ==========================================================================
    doc = revit.doc
    uidoc = revit.uidoc
    selection = revit.get_selection()

    # PHASE 1: UNIFIED SOLID UNION EXTRACTION & BOUNDARY SEPARATION
    # ==============================================================================
    UI.TaskDialog.Show("Brick Layout", "Select your walls, then click Finish on the Options Bar.")

    selected_elements = list(selection)
    walls = [el for el in selected_elements if isinstance(el, Wall)]

    if not walls:
        UI.TaskDialog.Show("Error", "No valid Walls were selected. Execution aborted.")
        script.exit()

    # Extracted thickness from the first wall instance safely
    wall_thickness_feet = walls[0].WallType.Width

    # 1. Fuse ALL wall solids to dissolve butt joints and calculate corners
    geo_options = Options()
    geo_options.ComputeReferences = False
    geo_options.DetailLevel = ViewDetailLevel.Fine
    master_solid = None

    for wall in walls:
        geo_elem = wall.get_Geometry(geo_options)
        if geo_elem is None:
            continue
        for geo_obj in geo_elem:
            if isinstance(geo_obj, Solid) and geo_obj.Volume > 0:
                if master_solid is None:
                    master_solid = geo_obj
                else:
                    try:
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

    # Tolerance configuration for downstream sorting engine
    tol = 0.05
    def same(p1, p2):
        return p1.DistanceTo(p2) < tol

    # --- TOPOLOGICAL MORPHOLOGY ANALYSIS & LOOP SPLITTING ---
    # Select the main analytical curve loop container
    selected_loop = all_loops[0] if len(all_loops) == 1 else max(all_loops, key=lambda l: l.GetExactLength())

    # Convert the CurveLoop container into an iterable list of individual Curve objects
    loop_curves = [c for c in selected_loop]
    num_curves = len(loop_curves)

    # Find the indices of the end-caps matching the wall thickness
    cap_indices = []
    for idx, curve in enumerate(loop_curves):
        if abs(curve.Length - wall_thickness_feet) < 0.083: # 1-inch variance tolerance
            cap_indices.append(idx)

    # If we don't find exactly two end caps, it's a closed structural loop layout
    if len(all_loops) > 1 or len(cap_indices) != 2:
        is_closed_loop_layout = True
        print("Morphology Identified: Closed Loop. Isolating exterior perimeter by area scaling.")
        outer_loop = max(all_loops, key=lambda l: l.GetExactLength())
        target_curves = [curve for curve in outer_loop]

    else:
        is_closed_loop_layout = False
        print("Morphology Identified: Open String. Splitting parallel tracks topologically...")

        cap_indices.sort()
        idx1 = cap_indices[0]
        idx2 = cap_indices[1]

        # Extract the two long continuous tracks sitting between the end caps
        track_1 = loop_curves[idx1 + 1 : idx2]
        track_2 = loop_curves[idx2 + 1 :] + loop_curves[:idx1]

        # Clean up empty tracks or edge cases
        lines_side_a = [c for c in track_1 if abs(c.Length - wall_thickness_feet) >= 0.083]
        lines_side_b = [c for c in track_2 if abs(c.Length - wall_thickness_feet) >= 0.083]

        if not lines_side_a or not lines_side_b:
            UI.TaskDialog.Show("Geometry Error", "Could not split the profile loop into distinct tracks.")
            script.exit()

        # 3. Native Visual Highlighting using View Detail Lines
        created_line_ids = []

        # CONFIGURING CRISP BRIGHT PINK GRAPHICS OVERRIDE
        thick_override = OverrideGraphicSettings()
        thick_override.SetProjectionLineColor(Color(255, 0, 255)) # Hot Pink (Magenta)
        thick_override.SetProjectionLineWeight(4) # Clean thickness definition

        t_draw = Transaction(doc, "Draw Temp Track Highlight")
        t_draw.Start()
        for curve in lines_side_a:
            try:
                p_start = curve.GetEndPoint(0)
                p_end = curve.GetEndPoint(1)
                view_curve = Line.CreateBound(XYZ(p_start.X, p_start.Y, 0), XYZ(p_end.X, p_end.Y, 0))

                d_line = doc.Create.NewDetailCurve(doc.ActiveView, view_curve)
                created_line_ids.append(d_line.Id)

                # Apply the hot pink override parameters directly onto the active view layout
                doc.ActiveView.SetElementOverrides(d_line.Id, thick_override)
            except Exception:
                pass
        t_draw.Commit()

        # Clear the active selection entirely so Revit doesn't color over the pink with a blue mask
        uidoc.Selection.SetElementIds(List[ElementId]())
        uidoc.RefreshActiveView()

        # 4. Pure Programmatic WPF Windows Object Generation
        panel = Window()
        panel.Title = "Track Selector"
        panel.Height = 150
        panel.Width = 420
        panel.WindowStartupLocation = WindowStartupLocation.CenterScreen
        panel.Topmost = True
        panel.ResizeMode = panel.ResizeMode.NoResize

        # Create root structural stack layout container
        main_layout = StackPanel()
        main_layout.Margin = Thickness(15)

        # Set up text label description
        txt_lbl = TextBlock()
        txt_lbl.Text = "Is the PINK HIGHLIGHTED track the EXTERIOR side?"
        txt_lbl.FontWeight = FontWeights.Bold
        txt_lbl.FontSize = 13
        txt_lbl.TextWrapping = txt_lbl.TextWrapping.Wrap
        txt_lbl.Margin = Thickness(0, 0, 0, 15)
        main_layout.Children.Add(txt_lbl)

        # Construct two-wide split row matrix layout
        btn_grid = Grid()
        col1 = ColumnDefinition()
        col2 = ColumnDefinition()
        btn_grid.ColumnDefinitions.Add(col1)
        btn_grid.ColumnDefinitions.Add(col2)

        state = {"approved": True}

        def click_yes(sender, e):
            state["approved"] = True
            panel.Close()

        def click_no(sender, e):
            state["approved"] = False
            panel.Close()

        # Create Button A
        btn_yes = Button()
        btn_yes.Content = "Yes, Use Highlighted Track"
        btn_yes.Height = 30
        btn_yes.Margin = Thickness(0, 0, 5, 0)
        btn_yes.Click += click_yes
        Grid.SetColumn(btn_yes, 0)
        btn_grid.Children.Add(btn_yes)

        # Create Button B
        btn_no = Button()
        btn_no.Content = "No, Use Opposite Track"
        btn_no.Height = 30
        btn_no.Margin = Thickness(5, 0, 0, 0)
        btn_no.Click += click_no
        Grid.SetColumn(btn_no, 1)
        btn_grid.Children.Add(btn_no)

        main_layout.Children.Add(btn_grid)
        panel.Content = main_layout

        # Launch window modelessly so the active view rendering engine functions beneath it
        panel.ShowDialog()
        user_selection_is_side_a = state["approved"]

        # 5. Instant Database Cleanup
        t_clean = Transaction(doc, "Clean Temp Highlights")
        t_clean.Start()
        for l_id in created_line_ids:
            try:
                doc.Delete(l_id)
            except:
                pass
        t_clean.Commit()
        uidoc.RefreshActiveView()

        # 6. Assign target track side curves based on user choice
        if user_selection_is_side_a:
            target_curves = lines_side_a
        else:
            print("User selected opposite track. Generating mirror track from primary track sequence...")
            target_curves = []

            # Project the cleanly sequenced layout of Side A across the wall thickness
            for curve in lines_side_a:
                p_start = curve.GetEndPoint(0)
                p_end = curve.GetEndPoint(1)

                segment_dir = (p_end - p_start).Normalize()
                normal = XYZ(-segment_dir.Y, segment_dir.X, 0.0)
                test_shift = p_start + (normal * wall_thickness_feet)

                # Distance check maps out which direction side B sits natively
                is_correct_direction = False
                for b_curve in lines_side_b:
                    if b_curve.Distance(test_shift) < 0.1:
                        is_correct_direction = True
                        break

                if not is_correct_direction:
                    normal = -normal

                # Construct a clean, identically sequenced boundary layout curve
                new_p_start = p_start + (normal * wall_thickness_feet)
                new_p_end = p_end + (normal * wall_thickness_feet)
                target_curves.append(Line.CreateBound(new_p_start, new_p_end))

    # BRIDGE LINK: Proximity search maps the unlinked profile curve directly back to its source Wall object
    raw_edges = []
    for c in target_curves:
        p_start = c.GetEndPoint(0)
        p_end = c.GetEndPoint(1)
        mid_point = c.Evaluate(0.5, True)

        matched_wall = None
        closest_dist = float('inf')
        for w in walls:
            if isinstance(w.Location, LocationCurve):
                dist = w.Location.Curve.Distance(mid_point)
                if dist < closest_dist:
                    closest_dist = dist
                    matched_wall = w

        # Retain the physical object element reference alongside the raw points
        raw_edges.append({
            "Wall": matched_wall,
            "Start": p_start,
            "End": p_end
        })

    # ==============================================================================
    # PHASE 2: TOPOLOGICAL SORTING ENGINE (Maintains Reference Links)
    # ==============================================================================
    if not raw_edges:
        print("Error: No raw edges collected from profile extraction.")
        script.exit()

    unused = raw_edges[:] 
    current = unused.pop(0) 
    ordered_data = [current] 
    current_point = current["End"] 

    while unused:
        found = False
        for i, edge in enumerate(unused):
            s = edge["Start"]
            e = edge["End"]
            w = edge["Wall"]
            if same(s, current_point):
                ordered_data.append({"Wall": w, "Start": s, "End": e}) 
                current_point = e 
                unused.pop(i) 
                found = True 
                break
            elif same(e, current_point):
                # Reverse vector orientation inline to preserve continuous flow direction
                ordered_data.append({"Wall": w, "Start": e, "End": s}) 
                current_point = s 
                unused.pop(i) 
                found = True 
                break

        # CRITICAL: This break must sit inside the while loop, aligned with the 'for' loop
        if not found: 
            break

    # Extract the sorted endpoints strictly for calculation downstream
    ordered = [(item["Start"], item["End"]) for item in ordered_data]
    
    # PRINT DIAGNOSTIC - CAN BE DELETED LATER
    print("\n===== ORDERED EDGES =====")
    for i, (s, e) in enumerate(ordered):
        print(
            "Edge {}: ({:.1f}, {:.1f}) -> ({:.1f}, {:.1f})".format(
                i,
                s.X * 304.8, s.Y * 304.8,
                e.X * 304.8, e.Y * 304.8
            )
        )
    # ==============================================================================
    # PHASE 3 & 4: AUTOMATIC VECTOR CORNER ANALYSIS & BRICK CONDITIONS
    # ==============================================================================

    num_edges = len(ordered)
    EDGES = []

    first_point = ordered[0][0]
    last_point = ordered[-1][1]
    is_closed_loop_layout = same(first_point, last_point) 

    def cross_product_z(p1, p2, p3):
        v1_x = p2.X - p1.X
        v1_y = p2.Y - p1.Y
        v2_x = p3.X - p2.X
        v2_y = p3.Y - p2.Y
        return (v1_x * v2_y) - (v1_y * v2_x)

    user_direction_override = False 

    if is_closed_loop_layout:
        total_turn_sign = 0 
        for i in range(num_edges):
            edge_curr = ordered[i]
            edge_next = ordered[(i + 1) % num_edges]
            cp_z = cross_product_z(edge_curr[0], edge_curr[1], edge_next[0])
            if cp_z > 0: total_turn_sign += 1
            elif cp_z < 0: total_turn_sign -= 1
        is_ccw = total_turn_sign > 0 
    else:
        is_ccw = user_direction_override 

    for i in range(num_edges):
        edge_curr = ordered[i]
        pt_start = edge_curr[0]
        pt_end = edge_curr[1]

        dx_mm = (pt_end.X - pt_start.X) * 304.8
        dy_mm = (pt_end.Y - pt_start.Y) * 304.8
        length_mm = math.sqrt(dx_mm**2 + dy_mm**2)

        if i == 0 and not is_closed_loop_layout:
            start_is_external = False 
            start_is_open = True
        else:
            edge_prev = ordered[(i - 1) % num_edges] 
            cp_start_z = cross_product_z(edge_prev[0], edge_prev[1], pt_end)
            start_is_external = cp_start_z > 0 if is_ccw else cp_start_z < 0
            start_is_open = False

        if i == num_edges - 1 and not is_closed_loop_layout:
            end_is_external = False
            end_is_open = True
        else:
            edge_next = ordered[(i + 1) % num_edges]
            cp_end_z = cross_product_z(pt_start, pt_end, edge_next[1])
            end_is_external = cp_end_z > 0 if is_ccw else cp_end_z < 0
            end_is_open = False

        if (i == 0 or i == num_edges - 1) and not is_closed_loop_layout:
            if num_edges == 1: brick_condition = "Co-" 
            elif i == 0: brick_condition = "Co-" if end_is_external else "Co"
            else: brick_condition = "Co-" if start_is_external else "Co"
        else:
            if start_is_external and end_is_external: brick_condition = "Co-"   
            elif (start_is_external and not end_is_external) or (not start_is_external and end_is_external): brick_condition = "Co"    
            else: brick_condition = "Co+"   

        wall_info = {
            "Wall Object": ordered_data[i]["Wall"], # Injects physical wall object reference safely into data map
            "Points List": [(pt_start.X * 304.8, pt_start.Y * 304.8, pt_start.Z * 304.8), 
                            (pt_end.X * 304.8, pt_end.Y * 304.8, pt_end.Z * 304.8)],
            "Length": length_mm,
            "Condition": brick_condition
        }
        EDGES.append(wall_info)

    # ==============================================================================
    # PHASE 5: RESIZE LENGTH CALCULATION FUNCTION & HORIZONTAL PROJECTIONS
    # ==============================================================================
    def resize(length, condition):
        if condition == "Co-": grid_length = length + 10
        elif condition == "Co+": grid_length = length - 10
        else: grid_length = length

        half_brick_units = round(grid_length / 112.5) 

        if condition == "Co-": return (half_brick_units * 112.5 - 10)
        if condition == "Co+": return (half_brick_units * 112.5 + 10)
        if condition == "Co": return (half_brick_units * 112.5)

    EDGES_copy = []
    for edge in EDGES:
        EDGES_copy.append({
            "Wall Object": edge["Wall Object"],
            "Points List": list(edge["Points List"]),
            "Length": edge["Length"],
            "Condition": edge["Condition"]
        })

    # Resize leading segment (Segment 0)
    EDGES_copy[0]["Length"] = resize(EDGES[0]["Length"], EDGES[0]["Condition"])
    start_pt = EDGES_copy[0]["Points List"][0] 
    end_pt = EDGES[0]["Points List"][1] 
    dx = end_pt[0] - start_pt[0] 
    dy = end_pt[1] - start_pt[1] 

    if abs(dx) > abs(dy):
        direction = 1.0 if dx > 0 else -1.0
        new_end_x = start_pt[0] + (EDGES_copy[0]["Length"] * direction)
        EDGES_copy[0]["Points List"][1] = (new_end_x, start_pt[1], start_pt[2])
    else:
        direction = 1.0 if dy > 0 else -1.0
        new_end_y = start_pt[1] + (EDGES_copy[0]["Length"] * direction)
        EDGES_copy[0]["Points List"][1] = (start_pt[0], new_end_y, start_pt[2])

    prev_end_pt = EDGES_copy[0]["Points List"][1]

    # Sequential array projection loop
    for i in range(1, len(EDGES_copy)):
        EDGES_copy[i]["Points List"][0] = prev_end_pt
        EDGES_copy[i]["Length"] = resize(EDGES[i]["Length"], EDGES[i]["Condition"])
        orig_start = EDGES[i]["Points List"][0]
        orig_end = EDGES[i]["Points List"][1]
        dx = orig_end[0] - orig_start[0]
        dy = orig_end[1] - orig_start[1]

        if abs(dx) > abs(dy):
            direction = 1.0 if dx > 0 else -1.0
            new_end_x = EDGES_copy[i]["Points List"][0][0] + (EDGES_copy[i]["Length"] * direction)
            EDGES_copy[i]["Points List"][1] = (new_end_x, EDGES_copy[i]["Points List"][0][1], EDGES_copy[i]["Points List"][0][2])
        else:
            direction = 1.0 if dy > 0 else -1.0
            new_end_y = EDGES_copy[i]["Points List"][0][1] + (EDGES_copy[i]["Length"] * direction)
            EDGES_copy[i]["Points List"][1] = (EDGES_copy[i]["Points List"][0][0], new_end_y, EDGES_copy[i]["Points List"][0][2])

        prev_end_pt = EDGES_copy[i]["Points List"][1]

    # ==============================================================================
    # PHASE 6: FINAL PRINT REPORT
    # ==============================================================================
    print("\n--- BRICK COORDINATOR PROCESSED OUTPUT ---")
    for idx in range(len(EDGES)):
        print("Wall Segment [{}]:".format(idx))
        print("  -> Original Length : {:.1f}mm".format(EDGES[idx]["Length"]))
        print("  -> Corner Condition: {}".format(EDGES[idx]["Condition"]))
        print("  -> Target Brick Dim: {:.1f}mm".format(EDGES_copy[idx]["Length"]))

    # ==============================================================================
    # PHASE 7: AUTOMATIC PHYSICAL MODEL REPOSITIONING (UNIVERSAL SHAPE ENGINE)
    # ==============================================================================
    # Open a database transaction to push changes into the active Revit document
    t_move = Transaction(doc, "Reposition and Co-ordinate Walls")
    t_move.Start()

    try:
        for edge_data in EDGES_copy:
            wall = edge_data["Wall Object"]
            if wall is None:
                continue

            # 1. Pull the newly calculated exterior brick target coordinates from Phase 5
            # Explicitly isolate the start node [0] and end node [1] from the sequence
            start_mm = edge_data["Points List"][0]
            end_mm = edge_data["Points List"][1]

            # 2. Convert exterior metric coordinate values back into native Revit Imperial Feet
            pt_start_ext = XYZ(start_mm[0] / 304.8, start_mm[1] / 304.8, start_mm[2] / 304.8)
            pt_end_ext = XYZ(end_mm[0] / 304.8, end_mm[1] / 304.8, end_mm[2] / 304.8)

            # 3. Compute the 2D direction vector of this wall segment
            dir_vector = (pt_end_ext - pt_start_ext).Normalize()

            # 4. Generate a perpendicular normal vector 
            perpend_normal = XYZ(dir_vector.Y, -dir_vector.X, 0.0)

            # 5. Calculate half the wall thickness to find the centerline shift distance
            half_thickness_feet = wall.WallType.Width / 2.0

            # 6. DYNAMIC TEST: Check if this normal points towards the wall core or away from it
            test_shift_pt = pt_start_ext + (perpend_normal * half_thickness_feet)

            wall_loc = wall.Location
            if isinstance(wall_loc, LocationCurve):
                # Measure distance from our test point to the actual existing wall centerline axis line
                dist_to_existing_center = wall_loc.Curve.Distance(test_shift_pt)

                # If the shifted point is further away than the full thickness of the wall, 
                # it means the vector pointed OUT into empty space instead of IN towards the wall core.
                if dist_to_existing_center > wall.WallType.Width:
                    # Flip the vector 180 degrees to correct it dynamically
                    perpend_normal = XYZ(-dir_vector.Y, dir_vector.X, 0.0)

            # 7. Shift the exterior target points using the verified normal to find the true centerline
            pt_start_center = pt_start_ext + (perpend_normal * half_thickness_feet)
            pt_end_center = pt_end_ext + (perpend_normal * half_thickness_feet)

            # 8. Build the new bounded line geometry along the centerline axis
            new_line = Line.CreateBound(pt_start_center, pt_end_center)

            # 9. Force the Wall location parameter reference back to Wall Centerline (Value 0)
            loc_param = wall.get_Parameter(BuiltInParameter.WALL_KEY_REF_PARAM)
            if loc_param and not loc_param.IsReadOnly:
                loc_param.Set(0) 

            # 10. Overwrite the location line curve property to snap the wall cleanly into place
            wall_loc.Curve = new_line

        t_move.Commit()
        print("\n[SUCCESS]: Physical walls have been automatically adjusted to match brick dimensions.")
        uidoc.RefreshActiveView()

    except Exception as e:
        t_move.RollBack()
        UI.TaskDialog.Show("Execution Error", "Failed to reposition structural walls: {}".format(str(e)))
