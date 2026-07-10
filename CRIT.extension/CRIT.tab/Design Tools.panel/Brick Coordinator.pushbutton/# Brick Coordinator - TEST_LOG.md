# Brick Coordinator - Development Test Log

---

# Commit 004

---

## Git Commit #

004

---

## Commit Message

Refactor non-flipped Part F to use local corner classification

---

## Change Made

Refactored the non-flipped engine's Part F corner classification to match the flipped engine.

Changes include:

- Removed dependence on global clockwise/anti-clockwise loop direction when determining corner types.
- Replaced the conditional is_ccw corner tests with direct local cross-product classification.
- Both engines now classify corners using the same rule:
- Outside lies on the LEFT of the selected exterior track.
- A RIGHT turn (negative cross product) is an external corner.
- A LEFT turn (positive cross product) is an internal corner.
- The legacy is_ccw calculation has been retained temporarily but is no longer used by the corner-classification logic.

---

## Reason for Change

Following the Parts B–E refactor, both the flipped and non-flipped engines now produce the same geometric invariant before entering Part F.

This made it possible to replace the remaining orientation-dependent logic with the same local corner-classification algorithm already proven in the flipped engine.

The aim is to eliminate dependence on whole-loop orientation and instead classify each corner purely from local geometry.

---

# Revit Test Results

## FLIPPED (Exterior on Left)

### Closed Loop - Clockwise
[x]

Error / Notes:

Corner classification correct.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Corner classification correct.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

### Open Loop
[x]

Error / Notes:

Corner classification correct.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

## NON-FLIPPED (Exterior on Right)

### Closed Loop - Clockwise
[x]

Error / Notes:

Corner classification correct.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Corner classification correct.

The previous "elements are reversed" error no longer occurs.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

### Open Loop
[x]

Error / Notes:

Corner classification correct.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

## Overall Result

The same local corner-classification algorithm now works correctly for all tested scenarios in both the flipped and non-flipped engines.

The previous dependency on global loop orientation is no longer required for executable corner-classification logic.

The earlier failure affecting non-flipped anti-clockwise closed loops has been resolved by adopting the same local cross-product rule used by the flipped engine.

This establishes a common geometric rule across both engines:

- Outside lies on the LEFT of the selected sorted exterior track.
- Wall core lies on the RIGHT of the selected sorted exterior track.
- RIGHT turn (negative cross product) = external corner.
- LEFT turn (positive cross product) = internal corner.

---

## Next Change / Hypothesis

Remove the now-obsolete global is_ccw calculation from the non-flipped engine and verify that all six test scenarios continue to pass.

If successful, both engines will use identical executable Part F logic, leaving only code cleanup and consolidation before moving on to the next stage.


## Commit Message

Refactor non-flipped Part F to use local corner classification


