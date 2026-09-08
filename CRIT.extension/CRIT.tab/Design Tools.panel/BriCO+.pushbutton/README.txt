# CRiT: Brick Coordinator

**CRiT: Brick Coordinator** is a pyRevit tool that automatically adjusts Revit wall geometry to brick-coordinated dimensions while accounting for external corners, internal corners and open wall ends.

The tool is intended to automate a repetitive piece of architectural coordination that would otherwise require the designer to manually calculate suitable brick dimensions and adjust individual walls while maintaining the overall wall layout.

Rather than simply rounding every wall to a standard module, Brick Coordinator analyses the geometry of the selected wall run, determines the condition at each end of every wall and calculates the appropriate brick-coordinated length.

The current prototype supports:

* Open wall runs
* Closed wall loops
* External corners
* Internal corners
* Open wall ends
* Clockwise and anti-clockwise layouts
* Flipped and non-flipped Revit walls
* Automatic physical repositioning of the selected Revit walls

---

# Core Concept: Brick Coordination

Brickwork dimensions depend not only on the nominal brick module but also on the condition occurring at each end of a wall.

Brick Coordinator therefore assigns each wall one of three coordination conditions:

* **Co**
* **Co+**
* **Co-**

These represent different relationships between the wall dimension and the brick coordination grid.

The current tool uses a **112.5 mm half-brick module** and applies a ±10 mm adjustment where required by the wall's corner condition.

The general principle is:

**Analyse wall geometry → identify corner conditions → assign brick condition → calculate coordinated length → reposition Revit walls**

This means brick coordination is derived from the geometry of the wall layout rather than requiring the user to calculate each wall manually.

---

# 1. Select Walls

The user selects the Revit walls to be coordinated before running the tool.

Brick Coordinator retrieves the selected Wall elements and uses their physical Revit geometry as the starting point for the analysis.

The current prototype is intended to operate on a connected wall run rather than arbitrary unrelated walls.

---

# 2. Extract Wall Geometry

Brick Coordinator extracts the solid geometry of the selected walls and performs Boolean union operations to combine them into a single representation of the wall layout.

The bottom face of the resulting solid is then used to extract the wall boundary geometry.

This allows the tool to work from the actual physical faces of the walls rather than relying solely on their Revit LocationCurves.

The resulting geometry represents the two sides of the selected wall run.

---

# 3. Detect Open or Closed Layout

Brick Coordinator automatically determines whether the selected walls form:

* an **open wall run**, or
* a **closed wall loop**.

For a closed layout, the fused wall geometry produces two perimeter loops representing the two sides of the wall.

For an open run, the boundary also contains the wall end caps. The tool identifies these using the wall thickness and separates the remaining geometry into the two continuous wall-face tracks.

The result in either case is two candidate tracks representing opposite sides of the selected walls.

---

# 4. Confirm Exterior Face

Brick coordination depends on knowing which physical wall face represents the exterior.

Rather than relying on Revit wall flip state or wall drawing direction, Brick Coordinator asks the user to confirm the exterior geometrically.

One candidate track is temporarily highlighted in **pink** within the active Revit view.

The user is asked:

> Is the pink highlighted track the exterior side?

The user can either:

* accept the highlighted track; or
* select the opposite track.

The temporary geometry is then removed.

From this point onwards, the algorithm operates on the confirmed exterior wall face.

This allows the main coordination algorithm to work consistently regardless of whether the original Revit walls are flipped or non-flipped.

---

# 5. Match and Sort Wall Edges

Each curve in the selected exterior track is matched back to its corresponding original Revit Wall element.

The tool does this by comparing the exterior edge geometry with the LocationCurves of the selected Revit walls and identifying the closest matching wall.

The wall reference is then stored together with the edge geometry and carried through the remainder of the algorithm.

The selected exterior edges are also sorted into a continuous sequence.

Where necessary, individual edge directions are reversed so that the complete exterior track follows one consistent direction.

This produces an ordered representation of the wall layout in which each edge retains a reference to the Revit Wall that it represents.

---

# 6. Analyse Corner Geometry

Brick Coordinator analyses the relationship between consecutive exterior edges using vector geometry.

For each junction, a signed 2D cross product is calculated to determine whether the exterior track turns left or right.

Because the sorted exterior track is oriented so that the outside lies consistently on its left:

* a **right turn** represents an external corner;
* a **left turn** represents an internal corner.

Open wall ends are handled separately because no adjacent wall exists at those locations.

Each wall can therefore be classified according to the condition occurring at its start and end.

---

# 7. Assign Brick Condition

The start and end conditions are used to assign the appropriate brick coordination condition to each wall.

The current system uses:

* **Co-** where the geometry requires the reduced coordination condition
* **Co** for the standard coordination condition
* **Co+** where the geometry requires the increased coordination condition

The exact condition depends on the combination of external corners, internal corners and open ends occurring at the two ends of the wall.

This allows the coordination rule to be derived automatically from the wall geometry rather than selected manually by the user.

---

# 8. Calculate Brick-Coordinated Lengths

Once the condition has been assigned, Brick Coordinator calculates the nearest suitable brick-coordinated dimension.

The current prototype uses a **112.5 mm half-brick module**.

The resizing calculation accounts for the assigned:

* Co
* Co+
* Co-

condition before rounding the wall to the nearest module.

The walls are processed sequentially.

The first resized edge retains its original start point. Each subsequent edge begins from the newly calculated endpoint of the preceding edge.

This allows dimensional changes to propagate through the connected wall run while maintaining continuity between walls.

The current resizing engine assumes horizontal or vertical wall edges.

---

# 9. Calculate New Wall Centrelines

The brick coordination calculations operate on the selected **exterior wall face**, but Revit walls are ultimately repositioned using their LocationCurves.

Brick Coordinator therefore converts each resized exterior edge back into the appropriate wall centreline.

For each wall, the tool:

* converts the resized edge coordinates into Revit internal units;
* calculates the direction of the resized exterior edge;
* calculates a perpendicular vector;
* creates test points on either side of the exterior edge at half the wall thickness;
* compares these test points with the wall's existing LocationCurve;
* determines which side of the exterior edge contains the wall centreline;
* offsets the resized edge by half the wall thickness in the correct direction;
* creates a new Revit Line representing the target centreline.

This approach avoids needing to infer centreline direction from Revit wall flip state.

---

# 10. Update the Revit Model

Once the target centrelines have been calculated, Brick Coordinator physically updates the selected Revit walls.

Wall joins are temporarily disabled while the geometry is being changed to reduce interference from Revit's automatic wall-join behaviour.

For each wall, the tool then:

* sets the wall Location Line reference to Wall Centreline;
* normalises flipped walls where required;
* assigns the newly calculated LocationCurve.

Wall joins are subsequently re-enabled.

The complete operation is performed within a Revit transaction so that failed model modifications can be rolled back.

The result is a physically adjusted Revit wall layout coordinated to the calculated brick dimensions.

---

# Current Algorithm

At a high level, the current Brick Coordinator workflow is:

**Select walls**

↓

**Fuse wall geometry**

↓

**Extract wall boundaries**

↓

**Detect open / closed layout**

↓

**Separate the two wall-face tracks**

↓

**User confirms exterior face**

↓

**Match exterior edges to Revit walls**

↓

**Sort exterior track**

↓

**Analyse internal / external corners**

↓

**Assign Co / Co+ / Co- conditions**

↓

**Calculate coordinated wall lengths**

↓

**Recalculate wall centrelines**

↓

**Update physical Revit walls**

---

# Handling Revit Wall Flip State

An important development goal has been to remove wall flip state from the main brick-coordination algorithm.

Earlier versions required separate logic for flipped and non-flipped walls.

The current architecture instead establishes the exterior wall face geometrically and carries the corresponding Revit Wall reference through the processing pipeline.

As a result, the geometry, corner-classification and resizing stages do not need separate flipped/non-flipped algorithms.

Wall flip state is only considered when the final calculated geometry is applied back to the Revit model.

This significantly reduces duplicated logic and allows the same processing engine to operate on:

* flipped walls;
* non-flipped walls;
* clockwise layouts;
* anti-clockwise layouts.

---

# Current Regression Testing

The current prototype is tested against six standard geometry cases.

## Flipped Walls

* Closed Loop — Clockwise
* Closed Loop — Anti-clockwise
* Open Loop

## Non-Flipped Walls

* Closed Loop — Clockwise
* Closed Loop — Anti-clockwise
* Open Loop

Following the first full architectural refactor, all six regression tests produce successful wall repositioning.

These tests are used after each significant refactor to verify that changes to the code structure have not altered the existing geometric behaviour.

---

# Current Development Status

The first architectural refactoring pass of Brick Coordinator is now complete.

The original procedural script has progressively been reorganised into helper functions representing clearer individual responsibilities, including:

* wall boundary extraction;
* open/closed layout detection and track separation;
* exterior-track confirmation;
* wall/edge matching;
* track sorting;
* vector corner analysis;
* brick-condition assignment;
* brick-dimension resizing;
* target centreline calculation;
* Revit wall modification.

The main focus of this first refactor has been **behaviour preservation**.

Changes have therefore concentrated on:

* removing duplicated algorithms;
* separating responsibilities;
* improving function interfaces;
* making the main workflow easier to understand;
* reducing dependence on flipped/non-flipped branching;
* maintaining identical Revit output throughout the refactor.

---

# Current Limitations / Areas for Review

The current version is a working prototype and still contains several assumptions and areas requiring further development.

These include:

* The resizing engine currently distinguishes horizontal and vertical wall edges rather than resizing arbitrary angled walls.
* Wall thickness is initially derived from the first selected wall; layouts containing different wall thicknesses require further investigation.
* Open-run end-cap detection currently uses wall thickness and a tolerance.
* The sorting engine currently contains fallback behaviour for unsorted segments that should potentially become an explicit error.
* Active-view compatibility should be checked before creating temporary Detail Curves.
* Error handling should be separated more clearly from geometric calculation.
* Location Line parameter error handling requires review.
* Closed loops with irregular geometry require further testing, particularly where accumulated resizing affects the final junction.

These are deliberately being retained as identifiable development tasks rather than adding complexity before the core architecture is stable.

---

# Next Development Stage

With the first architectural refactor complete, the next development pass should focus on tightening the existing implementation.

Potential work includes:

* reviewing helper-function interfaces;
* resolving outstanding TODOs;
* improving validation and error handling;
* reducing remaining diagnostic/debug code;
* consolidating repeated unit conversions;
* improving naming consistency;
* testing more complex and irregular wall layouts;
* investigating arbitrary angled walls;
* organising related helper functions into separate Python modules.

Once the internal architecture is sufficiently stable, the tool can move from a development script toward a more structured pyRevit application.

---

# Possible Future Development

The current tool coordinates the overall wall geometry.

A more complete Brick Coordinator could eventually extend this concept to other elements of masonry design and coordination.

Potential future features include:

* Door opening coordination
* Window opening coordination
* Automatic adjustment of opening positions to brick modules
* Automatic adjustment of opening widths
* Pier-width coordination
* Brick coursing in the vertical direction
* Coordination of sill, lintel and parapet levels
* Different brick sizes and masonry systems
* User-selectable bond / coordination rules
* Visual preview before committing wall changes
* Reporting walls or openings that cannot be coordinated within an acceptable tolerance
* User controls defining which walls or dimensions are allowed to move
* More comprehensive WPF user interface
* Automatic validation after coordination
* Integration with wider CRiT design checking

A future version could potentially distinguish between dimensions that are:

* **fixed** — must not move;
* **preferred** — should be retained where possible;
* **flexible** — may move to achieve brick coordination.

This would allow the tool to develop from a simple wall-resizing algorithm into a more general masonry coordination system.

---

# Wider CRiT Concept

Brick Coordinator represents one example of the wider **CRiT** concept: embedding architectural and construction knowledge directly into the design environment.

Rather than simply automating repetitive Revit operations, the tool encodes a specific piece of architectural knowledge — brick dimensional coordination — and applies it directly to live model geometry.

The longer-term principle is:

**Model geometry → understand design condition → apply construction rule → provide or implement coordinated solution**

This same approach could later be applied across other areas of CRiT, including:

* buildability;
* CDM / design risk;
* Building Regulations;
* embodied carbon;
* drawing production;
* design validation;
* construction coordination.

Brick Coordinator therefore acts both as a practical Revit automation tool and as a development exercise in translating architectural knowledge into structured, testable software.
