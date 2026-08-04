

Gen Thoughts:

1) specify ridge height in tool (so user could draw detail line for ridge at same level as roof footprint. Or user coudl simplyu draw footprint and ridge as detail lines on same level - then tool generates new roof from info. 
2) more complicated roofs? (multiple ridge lines..)



# Roof Slope Solver

A Revit automation tool that generates or updates a roof from a defined roof footprint and ridge line.

## Initial Scope

The first version will support:

- A single rectangular roof footprint
- A single straight ridge line
- Dual-pitch or hipped roof forms
- Asymmetrical roof pitches
- Native Revit roof output

## Workflow

### 1. Input

- Existing Revit roof object
- Ridge line, initially represented by a Revit detail line

### 2. Extract Geometry

Extract:

- The roof footprint curves from the roof sketch
- The footprint curve start and end coordinates
- The ridge start and end coordinates

### 3. Match Source Geometry

Retain the relationship between each extracted footprint curve and its corresponding original Revit roof edge.

This reference will later allow the calculated slope to be applied to the correct roof edge.

### 4. Classify and Package

Group the geometry into a list of dictionaries.

Each dictionary may contain:

```python
{
    "original_edge": ...,
    "face_coordinates": ...,
    "slope_angle": ...
}

Each dictionary represents one roof plane and preserves the relationship between:

- Original Revit footprint edge
- Calculated roof-plane geometry
- Calculated slope


### 5. Generate or Calculate

For each roof plane, either:

- Generate temporary face geometry and extract its angle, or
- Calculate the slope directly from the coordinates

Store the resulting slope angle in the corresponding dictionary.

### 6. Update or Create

Use the stored slope values to either:

- Update the correct edges of an existing Revit roof, or
- Create a new native Revit roof from the footprint and calculated slopes

Future Development:

User-Defined Ridge Height

Allow the user to define the ridge height within the tool.

This would allow the footprint and ridge to be drawn as detail lines on the same level, with the tool using the specified ridge height to calculate the roof slopes.

Detail-Line Input:

Allow the user to generate a new roof using only:

- Footprint detail lines
- Ridge detail line
- Ridge height

More Complex Roofs:

Investigate support for:

- Multiple ridge lines
- L-shaped footprints
- Valleys
- Intersecting roof forms

STRUCTURE NOTES:

Selected Model Lines
        ↓
1. Extract and classify input lines
        ↓
2. Build edge and ridge records
        ↓
3. Build roof-surface records
        ↓
4. Calculate slope for each surface
        ↓
5. Create roof and assign slopes
