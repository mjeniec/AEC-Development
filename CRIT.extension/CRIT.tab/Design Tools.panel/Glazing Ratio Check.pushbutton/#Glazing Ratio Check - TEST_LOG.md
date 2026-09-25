# Glazing Ratio Checker - Development Test Log

---

# Commit 001

---

## Git Commit #

001

---

## Commit Message

Calculate room glazing ratios from Revit model data

---

## Change Made

Created the first working prototype of the CRiT: Glazing Ratio Checker.

The tool now:

- Collects all Rooms in the active Revit model
- Extracts Room Number, Name and Floor Area
- Collects standard Window elements
- Calculates window area from Width × Height
- Associates windows with the rooms they serve
- Collects Curtain Wall Panels and includes their area
- Combines all identified glazing into a total glazing area for each room
- Calculates:

    Glazing Ratio = (Glazing Area / Room Area) × 100

The results are stored by room and output as a text report containing:

    Room Number
    Room Name
    Room Area
    Glazing Area
    Glazing Ratio

---

## Reason for Change

This establishes the basic data-processing workflow required for a room-based glazing checker.

The aim is to use information already contained within the Revit model to automatically assess the relationship between glazing and room floor area.

The current version provides the underlying calculation only.

Future development can combine this with additional information such as:

- Glazing orientation
- Cross-ventilation
- Geographic overheating risk
- Openable area
- External shading and overhangs

This would allow the tool to develop into an early-stage overheating and environmental design checker, including checks based on Approved Document O.

---

# Revit Test Results

## Room Data

[x]

All rooms in the House In Wood model are collected successfully.

Room Number, Name and Floor Area are returned correctly.

---

## Standard Windows

[x]

Standard windows are successfully collected and associated with the rooms they serve.

Multiple windows within the same room are correctly added together.

---

## Curtain Wall Glazing

[x]

Curtain Wall Panels are successfully collected and their areas can be added to the room glazing total.

---

## Glazing Ratio

[x]

The tool successfully calculates the total glazing area as a percentage of each room's floor area.

Example output:

    10 - BEDROOM 02
    Room Area: 15.41 sqm
    Glazing Area: 3.26 sqm
    Glazing Ratio: 21.16%

---

## Overall Result

The core room-based glazing calculation is operational.

The tool can now combine room data, standard windows and curtain wall glazing to produce a glazing-to-floor-area ratio for each room.

---

## Current Limitations

- Standard window area currently uses overall Width × Height rather than actual transparent glass area.
- Opaque curtain wall panels are not yet excluded automatically.
- The calculated ratio is not yet compared against regulatory or design criteria.
- More complex room, phase and glazing configurations require further testing.

---

## Next Change / Hypothesis

Add glazing orientation.

The tool should determine the facing direction of each window and curtain wall panel and classify glazing by orientation.

This can then be combined with glazing ratio data to begin implementing Approved Document O overheating checks.

Later development should also investigate automatic detection of external shading and roof overhang geometry.