# Glazing Ratio Checker - Development Test Log

---

# Commit 002

---

## Git Commit #

002

---

## Commit Message

Extract glazing orientation and identify most glazed façade

---

## Change Made

Extended the CRiT: Glazing Ratio Checker to determine the orientation of windows and curtain wall glazing.

The tool now:

- Determines the exterior-facing direction of each window and curtain wall panel
- Classifies glazing as North, East, South or West
- Stores glazing area by orientation for each room
- Calculates total glazing area by orientation for the building
- Identifies the façade with the greatest total glazing area
- Identifies the room with the greatest total glazing area

A helper function now determines the exterior-facing vector of each glazed element by:

- Finding the centre of the element
- Creating test points on either side of the glazing
- Checking which point lies within a Revit Room
- Returning the vector pointing towards the exterior

A second helper function classifies the resulting vector according to its dominant X or Y direction:

    +Y = North
    +X = East
    -Y = South
    -X = West

Room data now includes:

    glazing_by_orientation:
        North
        East
        South
        West

Whole-building glazing totals are stored separately in:

    total_glazing_area_by_orientation

The script also identifies:

    Most Glazed Elevation
    Largest Glazed Elevation Area
    Most Glazed Room
    Glazing Area of Most Glazed Room

---

## Reason for Change

Approved Document O uses the orientation of the façade with the greatest glazing area when selecting the appropriate simplified-method glazing limits.

The previous version calculated glazing-to-floor-area ratios but did not understand the direction in which the glazing faced.

This change introduces the geometric information required for a future Part O check.

The tool can now establish:

    Glazing Area
        +
    Room Association
        +
    Glazing Orientation
        ↓
    Glazing by Façade
        ↓
    Most Glazed Façade

It also identifies the most glazed room, which will be required for the separate Part O room-level glazing check.

---

# Revit Test Results

## Standard Window Orientation

[x]

Standard windows successfully return an exterior-facing direction.

The calculated orientations were checked against the House In Wood model and correspond with the expected building elevations.

---

## Curtain Wall Panel Orientation

[x]

Curtain Wall Panels successfully use the same orientation workflow as standard windows.

Panel areas are added both to:

- The appropriate room orientation total
- The appropriate whole-building orientation total

---

## Room Glazing by Orientation

[x]

Each room now reports its glazing area separately by North, East, South and West orientation.

Example:

    KITCHEN / DINING

    North: 8.81 sqm
    East: 0.00 sqm
    South: 6.44 sqm
    West: 11.14 sqm

---

## Whole-Building Glazing by Orientation

[x]

The script successfully totals glazing across the complete model by orientation.

Example output:

    North: 20.22 sqm
    East: 9.40 sqm
    South: 32.16 sqm
    West: 11.14 sqm

---

## Most Glazed Elevation

[x]

The script successfully identifies the elevation containing the greatest total area of glazing.

For the current House In Wood test model:

    Most Glazed Elevation: South

---

## Most Glazed Room

[x]

The script successfully compares room glazing totals and identifies the room containing the greatest actual area of glazing.

For the current test model:

    Most Glazed Room: Kitchen / Dining

---

## Overall Result

The tool can now determine both the quantity and orientation of glazing serving individual rooms and the dwelling as a whole.

The current workflow is:

    Rooms
        ↓
    Room Floor Areas
        ↓
    Windows + Curtain Wall Panels
        ↓
    Glazing Area
        ↓
    Room Association
        ↓
    Exterior-Facing Vector
        ↓
    North / East / South / West
        ↓
    Room Glazing by Orientation
        +
    Building Glazing by Orientation
        ↓
    Most Glazed Façade
        +
    Most Glazed Room

This provides the main geometric information required to begin implementing the Approved Document O simplified glazing check.

---

## Current Limitations

- Orientation is currently based on Revit Project North rather than True North.
- The exterior-side test currently uses a fixed 0.5 m offset from the glazing element.
- Standard window area still uses overall Width × Height rather than transparent glass area.
- Opaque curtain wall panels are not yet excluded automatically.
- Whole-dwelling floor area has not yet been calculated.
- The tool does not yet apply Approved Document O limits.
- Cross-ventilation and overheating-risk classification are not yet included.

---

## Next Change / Hypothesis

Implement the Approved Document O simplified glazing-area check.

The next version should introduce:

- Cross-ventilated / non-cross-ventilated selection
- Moderate-risk / high-risk location selection
- Approved Document O glazing-limit tables
- Whole-dwelling glazing ratio
- Most-glazed-room glazing ratio
- Automatic selection of the relevant Part O limits based on the most glazed façade
- Advisory compliance results for the whole-dwelling and most-glazed-room checks

Before the Part O assessment is treated as reliable, glazing orientation should also be corrected from Project North to True North.