# CRiT: Brick Coordinator — BriCO+

**BriCO+** is a pyRevit tool that automatically adjusts connected Revit walls to brick-coordinated dimensions.

Rather than simply rounding wall lengths to a standard module, the tool analyses the geometry of the selected wall run, identifies the condition at each wall end, assigns the appropriate brick coordination rule and physically repositions the Revit walls.

The aim is to automate a repetitive piece of architectural coordination that would otherwise require the designer to calculate suitable brick dimensions and adjust individual walls manually.

## Demo

[▶ Watch the BriCO+ Brick Coordinator demo](Media/brick-coordinator-demo.mp4)

The demonstration shows BriCO+ coordinating both a closed wall loop and an open wall run, with the Revit wall geometry automatically resized to suit the calculated brick dimensions.

---

## Current Capabilities

The current prototype supports:

- Open wall runs
- Closed wall loops
- External corners
- Internal corners
- Open wall ends
- Clockwise and anti-clockwise layouts
- Flipped and non-flipped Revit walls
- Automatic physical repositioning of selected Revit walls
- Native Revit wall output

---

## How It Works

At a high level, the current workflow is:

1. Select a connected wall run
2. Extract the physical wall boundary geometry
3. Detect whether the layout is open or closed
4. Identify and confirm the exterior wall face
5. Match the exterior geometry back to the original Revit walls
6. Analyse internal, external and open-end conditions
7. Assign the appropriate brick coordination rule
8. Calculate the nearest coordinated wall dimensions
9. Recalculate the corresponding wall centrelines
10.Update the physical Revit walls

The overall process can be summarised as:

Model geometry → understand wall condition → apply brick coordination rule → update Revit geometry

---

## Brick Coordination Logic

Brickwork dimensions depend not only on the nominal brick module but also on the condition occurring at each end of a wall.

BriCO+ therefore classifies each wall using one of three coordination conditions:

- Co
- Co+
- Co-

The current prototype uses a 112.5 mm half-brick module, with the appropriate adjustment applied according to the corner conditions at each end of the wall.

This allows the required brick dimension to be derived automatically from the wall geometry rather than selected manually by the user.

---

# Technical Development

The following sections document the current geometry-processing and Revit API approach used to develop the prototype.

## 1. Extract Wall Geometry

BriCO+ retrieves the solid geometry of the selected Revit walls and performs Boolean union operations to create a combined representation of the wall layout.

The bottom face of the resulting solid is then used to extract the wall boundary geometry.

This allows the tool to work from the actual physical faces of the walls rather than relying solely on their Revit `LocationCurves`.

---

## 2. Detect Open or Closed Layout

The tool automatically determines whether the selected walls form:

- an 'open wall run', or
- a 'closed wall loop'.

For a closed layout, the fused geometry produces two perimeter loops representing the two sides of the wall.

For an open run, the boundary also contains wall end caps. These are identified and removed so that the two continuous wall-face tracks can be isolated.

---

## 3. Confirm the Exterior Face

Brick coordination depends on knowing which physical wall face represents the exterior.

Rather than relying on Revit wall flip state or original drawing direction, BriCO+ identifies two candidate wall-face tracks geometrically.

One candidate track is temporarily highlighted in the active Revit view and the user confirms whether it represents the exterior.

From that point onwards, the coordination algorithm operates on the confirmed exterior wall face.

This allows the same processing logic to work regardless of whether individual Revit walls are flipped or non-flipped.

---

## 4. Match and Sort Wall Edges

Each edge in the confirmed exterior track is matched back to its corresponding original Revit Wall element.

The exterior edges are then sorted into a continuous sequence and, where necessary, reversed so that the complete track follows one consistent direction.

Each edge therefore retains a reference to the Revit wall that it represents throughout the calculation process.

---

## 5. Analyse Corner Geometry

The relationship between consecutive wall edges is analysed using vector geometry.

A signed 2D cross product is used to determine whether the exterior track turns left or right.

With the exterior consistently positioned on one side of the ordered track:

- one turn direction represents an 'external corner'
- the opposite direction represents an 'internal corner'
- open wall ends are handled separately

Each wall can therefore be classified according to the condition occurring at its start and end.

---

## 6. Assign Brick Condition

The start and end conditions are used to assign the appropriate:

- Co
- Co+
- Co-

brick coordination condition.

The required rule is therefore derived automatically from the physical wall geometry.

---

## 7. Calculate Coordinated Dimensions

Once the appropriate condition has been assigned, BriCO+ calculates the nearest suitable brick-coordinated dimension.

Walls are processed sequentially.

The first resized edge retains its original start position, while each subsequent edge begins from the newly calculated endpoint of the preceding wall.

This allows dimensional changes to propagate through the connected wall run while maintaining continuity between walls.

---

## 8. Recalculate Wall Centrelines

The brick calculations operate on the selected exterior wall face, but Revit walls are repositioned through their `LocationCurves`.

BriCO+ therefore converts each resized exterior edge back into the appropriate wall centreline.

For each wall, the tool:

- calculates the direction of the resized exterior edge
- calculates a perpendicular vector
- tests both possible centreline positions
- compares these against the existing wall location
- identifies the correct side of the exterior face
- offsets the resized edge by half the wall thickness
- creates the target Revit wall centreline

This avoids requiring separate centreline calculations for flipped and non-flipped walls.

---

## 9. Update the Revit Model

Once the target centrelines have been calculated, the selected Revit walls are physically updated.

Wall joins are temporarily disabled while the geometry is modified to reduce interference from Revit's automatic wall-join behaviour.

The tool then:

- sets the wall Location Line reference to Wall Centreline
- normalises flipped walls where required
- assigns the calculated `LocationCurve`
- re-enables wall joins

The complete operation takes place within a Revit transaction so that failed modifications can be rolled back.

---

## Handling Revit Wall Flip State

An important development goal has been to remove wall flip state from the main brick-coordination algorithm.

Earlier versions required separate processing for flipped and non-flipped walls.

The current approach instead establishes the exterior face geometrically and carries the corresponding Revit wall reference through the processing pipeline.

As a result, the main geometry, corner-classification and resizing stages can operate on:

- flipped walls
- non-flipped walls
- clockwise layouts
- anti-clockwise layouts

without requiring separate coordination algorithms.

---

## Regression Testing

The current prototype is tested against six standard geometry cases.

### Flipped Walls

- Closed Loop — Clockwise
- Closed Loop — Anti-clockwise
- Open Run

### Non-Flipped Walls

- Closed Loop — Clockwise
- Closed Loop — Anti-clockwise
- Open Run

Following the first architectural refactor, all six regression cases produce successful wall repositioning.

These tests are repeated after significant changes to help verify that refactoring has not altered the existing geometric behaviour.

---

## Development Status

The first architectural refactoring pass of BriCO+ is complete.

The original procedural script has progressively been reorganised into helper functions with clearer individual responsibilities, including:

- wall boundary extraction
- open/closed layout detection
- track separation
- exterior-face confirmation
- wall/edge matching
- track sorting
- vector corner analysis
- brick-condition assignment
- brick-dimension resizing
- target centreline calculation
- Revit wall modification

The main focus of the first refactor has been **behaviour preservation** while improving the structure and readability of the code.

---

## Current Limitations

The current version is a working prototype and still contains several assumptions and areas for further development.

These include:

- The resizing engine currently assumes horizontal or vertical wall edges
- Layouts containing different wall thicknesses require further investigation
- Open-run end-cap detection currently relies on wall thickness and a tolerance
- More irregular closed loops require additional testing
- Validation and error handling require further development
- Some remaining diagnostic/debug code should be removed
- The current interface is primarily a development interface rather than a finished user-facing tool

These limitations are being retained as identifiable development tasks rather than adding additional complexity before the core architecture is stable.

---

## Possible Future Development

A more complete version of BriCO+ could extend the same coordination approach to other aspects of masonry design.

Potential future features include:

- Door opening coordination
- Window opening coordination
- Automatic adjustment of opening positions to brick modules
- Automatic adjustment of opening widths
- Pier-width coordination
- Vertical brick coursing
- Coordination of sill, lintel and parapet levels
- Different brick sizes and masonry systems
- User-selectable coordination rules
- Visual preview before committing wall changes
- Reporting geometry that cannot be coordinated within an acceptable tolerance
- User controls defining which dimensions are fixed or allowed to move
- More comprehensive WPF user interface
- Automatic validation after coordination

A future version could potentially distinguish between dimensions that are:

- **Fixed** — must not move
- **Preferred** — should be retained where possible
- **Flexible** — may move to achieve brick coordination

This could allow the tool to develop from a wall-resizing prototype into a more general masonry coordination system.

---

# Wider CRiT Concept

Brick Coordinator is one example of the wider **CRiT** concept: embedding architectural and construction knowledge directly into the design environment.

Rather than simply automating repetitive Revit operations, BriCO+ attempts to encode a specific piece of architectural knowledge — brick dimensional coordination — and apply that knowledge directly to live model geometry.

The longer-term principle is:

**Model geometry → understand design condition → apply construction rule → provide or implement coordinated solution**

The same approach could potentially be applied to other areas of architectural design and coordination, including:

- Buildability
- CDM / design risk
- Building Regulations
- Embodied carbon
- Drawing production
- Design validation
- Construction coordination

BriCO+ therefore acts both as a practical Revit automation tool and as a development exercise in translating architectural knowledge into structured, testable software.