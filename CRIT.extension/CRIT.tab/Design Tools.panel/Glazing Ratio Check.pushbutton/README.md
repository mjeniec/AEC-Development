# Glazing Ratio Checker

A Revit / pyRevit design-checking tool for comparing the amount of glazing serving each room against the room floor area.

The current tool automatically extracts room areas and glazing areas from the Revit model, associates glazing with the rooms it serves, and calculates the glazing-to-floor-area ratio for each room.

The tool is intended as the starting point for a broader regulation-aware design assistant that can provide feedback on glazing, overheating, ventilation and daylight during design development.

## Demo

Demo to be added.

## Current Workflow

### 1. Collect rooms

The tool collects all Room elements in the active Revit model and extracts:

- Room number
- Room name
- Room floor area

The room information is stored in a dictionary which is used throughout the subsequent checks.

### 2. Collect standard windows

All placed elements in the Revit **Windows** category are collected.

For each window, the tool extracts the window type width and height and calculates the overall window area.

### 3. Associate windows with rooms

The Revit API `FromRoom` and `ToRoom` properties are used to determine which room each window serves.

The calculated window area is then added to the total glazing area stored against that room.

### 4. Collect curtain wall glazing

Curtain wall panels are collected separately from standard windows using the Revit **Curtain Wall Panels** category.

The area of each glazed panel is extracted and associated with the room on the internal side of the panel.

This allows standard windows and curtain wall glazing to contribute to the same overall glazing-area calculation.

### 5. Calculate glazing ratio

For each room, the total glazing area is compared with the room floor area:

    Glazing Ratio = (Total Glazing Area / Room Floor Area) × 100

The current report returns:

    Room Number
    Room Name
    Room Area
    Glazing Area
    Glazing Ratio

Example:

    09 - LIVING ROOM
    Room Area: 35.29 sqm
    Glazing Area: 10.60 sqm
    Glazing Ratio: 30.04%

## Current Scope

The current version supports:

- Revit Rooms
- Standard Revit window families
- Curtain wall glazing
- Automatic room association
- Total glazing area by room
- Glazing-to-floor-area percentage
- Text-based report output

The current calculation uses the overall width and height of standard window families and should therefore be treated as an approximate gross glazing area rather than a regulatory calculation of transparent glass area.

## Regulatory Development

The glazing ratio by itself should not be treated as a pass/fail daylight calculation.

Different UK regulations and design guidance use glazing and opening areas for different purposes.

### Approved Document O - Overheating

Approved Document O provides a particularly useful basis for future development of the tool.

The simplified method limits glazing area relative to floor area according to factors including:

- Orientation of the largest glazed facade
- Whether the dwelling is cross-ventilated
- Geographic overheating risk
- Total dwelling glazing
- Glazing within the most highly glazed room

The current tool already calculates one of the key inputs required for this assessment:

    Glazing Area / Floor Area

Future versions could determine the orientation of the glazing serving each room and compare the calculated ratio against the appropriate Approved Document O threshold.

Example future output:

    LIVING ROOM

    Floor Area:        35.29 sqm
    Glazing Area:      11.20 sqm
    Glazing Ratio:     31.74%
    Orientation:       South
    Cross Ventilated:  Yes

    Part O Limit:      30.00%

    Status: REVIEW
    Glazing exceeds simplified-method threshold.

### Approved Document F - Ventilation

Approved Document F introduces a related but different check based on the amount of openable area available for purge ventilation.

Future development could distinguish between:

    Total Glazing Area

and:

    Openable / Free Ventilation Area

Window parameters describing opening type, opening dimensions or opening angle could then be used to assess ventilation provision at room level.

### Approved Document L - Energy

Approved Document L also considers the overall quantity of glazing because glazing has a significant effect on heat loss and solar gain.

This should be treated as a separate whole-building or extension-level check rather than using a single glazing percentage as a target for individual rooms.

### Daylight

Glazing-to-floor-area ratio is only a useful early-stage proxy for daylight performance.

Actual daylight performance also depends on factors including:

- Orientation
- Window head height
- Room depth
- External obstructions
- Glass visible-light transmission
- Overhangs and shading
- Internal surface reflectance

Future development could therefore link the Revit model to more detailed daylight analysis rather than treating glazing ratio as a daylight compliance test.

## Future Development

### Solar Shading and Overhang Analysis

Future development could assess external shading geometry serving glazed elements.

The tool could identify roof overhangs, canopies or balconies above glazing and calculate parameters such as:

- Projection depth
- Vertical distance between glazing and shading element
- Solar cut-off angle
- Glazing orientation
- Percentage of glazing shaded at critical solar angles

This could support more detailed overheating assessment by recognising when glazing is protected by permanent external shading rather than considering glazing area alone.

For south-facing glazing, the tool could potentially test whether an overhang provides the solar cut-off geometry described in Approved Document O.

Longer-term development could combine:

    Glazing area
    + Orientation
    + Solar shading geometry
    + Glass g-value
    + Ventilation provision

to provide more meaningful early-stage overheating feedback.

### Orientation Detection

Automatically determine the orientation of each glazed element from its geometry.

For example:

    North
    North-East
    East
    South-East
    South
    South-West
    West
    North-West

This would allow the glazing calculation to be compared directly with orientation-dependent Part O limits.

### Approved Document O Checker

Add rules for the Approved Document O simplified method.

The tool could assess:

- Whole-dwelling glazing ratio
- Most-glazed room ratio
- Orientation
- Cross-ventilation
- Geographic overheating risk
- Maximum permitted glazing area

### Transparent Glass Area

Improve the current gross window-area calculation so that the actual transparent glazed area is measured rather than simply using overall family width × height.

This would allow window frames, mullions and opaque curtain panels to be excluded.

### Openable Area

Extract or calculate the openable portion of each window.

This could support:

- Approved Document O free-area checks
- Approved Document F purge ventilation checks
- Bedroom ventilation checks

### Room-Based Rules

Allow different checks to be applied depending on room type.

For example:

    Bedroom
    Living Room
    Kitchen
    Study
    Bathroom
    Classroom

### Revit Parameters

Write calculated results back into Room parameters such as:

    CRiT_GlazingArea
    CRiT_GlazingRatio
    CRiT_OverheatingStatus
    CRiT_VentilationStatus

These parameters could then be displayed in native Revit schedules and colour-coded using conditional formatting.

### User Interface

Develop a pyRevit interface allowing the user to:

- Select the applicable regulatory check
- Define location / overheating risk
- Specify whether the dwelling is cross-ventilated
- Review rooms requiring attention
- Navigate directly to affected rooms or glazing elements

## Structure

    Revit Rooms
         ↓
    1. Extract room number, name and floor area
         ↓
    Build room data dictionary
         ↓
    Standard Windows
         ↓
    2. Extract width and height
         ↓
    3. Calculate window area
         ↓
    4. Associate window with room
         ↓
    Curtain Wall Panels
         ↓
    5. Extract glazed panel area
         ↓
    6. Associate panel with room
         ↓
    Add all glazing to room total
         ↓
    7. Calculate glazing / floor area ratio
         ↓
    8. Generate room report
         ↓
    Future:
    Apply orientation + regulatory rules
         ↓
    Design feedback / Revit schedule