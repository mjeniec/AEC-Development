# Roof Slope Solver

A Revit/Dynamo form-finding tool for rapidly testing roof geometry from a defined roof footprint and ridge line.

The tool generates a native Revit roof and calculates the required slope of each roof plane from the position and elevation of the input geometry.

## Demo

[▶ Watch the Roof Slope Solver demo](Media/roof-slope-solver-demo.mp4)

The demonstration shows how the roof can be regenerated after changing the ridge position or elevation, allowing alternative roof forms to be tested quickly during design development.

## Current Workflow

### 1. Define the roof footprint

The roof footprint is drawn using Revit Model Lines with the **Roof Footprint** line style and placed at the required **Eaves Level**.

### 2. Define the ridge

The ridge is drawn using a Model Line with the **Ridge** line style and placed at the required **Ridge Level**.

### 3. Extract and classify geometry

The Dynamo graph identifies and separates the footprint and ridge geometry, extracting the coordinates required to construct each roof plane.

### 4. Generate roof surfaces

The relationship between the footprint edges and ridge is used to calculate the geometry and slope of each roof plane.

### 5. Create the Revit roof

A native Revit roof is generated from the footprint and the calculated slopes are assigned to the corresponding roof edges.

## Form Finding

Because the roof is generated from control geometry, the inputs can be modified and the roof regenerated.

For example:

- Move the ridge to quickly test alternative roof forms
- Change the ridge elevation to test different pitches and proportions
- Modify the footprint to explore alternative roof configurations

## Current Scope

The current version supports:

- A single rectangular roof footprint
- A single straight ridge line
- Dual-pitch and hipped roof forms
- Asymmetrical roof pitches
- Native Revit roof output

## Future Development

### Simplified Ridge Height Input

Allow the ridge height to be specified directly through the tool.

This would allow both the footprint and ridge to be drawn on the same level, with the tool applying the required vertical offset automatically.

### More Complex Roof Forms

Explore support for:

- Multiple ridge lines
- L-shaped footprints
- Valleys
- Intersecting roof forms

## Structure

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