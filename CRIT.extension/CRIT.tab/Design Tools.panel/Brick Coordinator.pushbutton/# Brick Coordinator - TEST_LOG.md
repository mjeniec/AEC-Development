# Brick Coordinator - Development Test Log

---

# Commit 007

---

## Git Commit #

007

---

## Commit Message

Refactor non-flipped Part H centreline offset selection

---

## Change Made

Refactored the non-flipped engine's Part H to replace the original single-candidate centreline offset selection with the same two-candidate comparison used by the flipped engine.

Changes include:

- Removed the single-candidate distance test used to determine whether the perpendicular vector should be reversed.
- Created two candidate centreline positions by offsetting the selected exterior track in both perpendicular directions.
- Measured the distance from each candidate position to the existing wall LocationCurve.
- Selected the candidate closest to the existing wall centreline.
- Introduced a correct_shift_vector variable to store the chosen offset direction.
- Updated the centreline calculation to use correct_shift_vector rather than the modified perpendicular vector.

---

## Reason for Change

The flipped engine already determines the centreline offset by comparing both possible offset directions and selecting whichever lies closest to the existing wall centreline.

Replacing the non-flipped engine's threshold-based single-candidate method with the same comparison removes one of the final behavioural differences between the two Part H implementations.

This approach is simpler, more explicit and independent of assumptions about the initial perpendicular direction.

---

# Revit Test Results

## FLIPPED (Exterior on Left)

### Closed Loop - Clockwise
[ ]

Error / Notes:

Not tested as no change.

---

### Closed Loop - Anti-clockwise
[ ]

Error / Notes:

Not tested as no change.

---

### Open Loop
[ ]

Error / Notes:

Not tested as no change.

---

## NON-FLIPPED (Exterior on Right)

### Closed Loop - Clockwise
[x]

Error / Notes:

Wall repositioning successful.

No behavioural differences observed.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Wall repositioning successful.

No behavioural differences observed.


---

### Open Loop
[x]

Error / Notes:

Wall repositioning successful.

No behavioural differences observed.

---

## Additional Testing – Irregular Closed Loops (L-shaped)

[x]

Error / Notes:

Multiple L-shaped closed loops of varying sizes and drawing directions were tested.

The majority repositioned and rejoined correctly.

One intermittent corner overlap was observed, but the behaviour could not be reproduced consistently and showed no clear relationship to wall direction, loop orientation or layout geometry.

The issue is therefore considered a separate intermittent reconstruction problem rather than a regression introduced by the two-candidate centreline selection algorithm.

---

## Overall Result

The two-candidate centreline selection algorithm works correctly for all standard non-flipped test scenarios.

The non-flipped engine now determines the centreline offset using the same explicit comparison method as the flipped engine, removing another substantive behavioural difference between the two Part H implementations.

An intermittent corner overlap remains on some irregular closed-loop layouts, but testing suggests this behaviour is unrelated to the centreline offset selection algorithm and should be investigated separately once both Part H implementations have been fully unified.

---

## Next Change / Hypothesis

Align the remaining Part H implementation details with the flipped engine by replacing the remaining non-flipped variable names and geometry terminology (pt_start_ext, dir_vector, perpend_normal, etc.) with the corresponding flipped-engine names.

Once the two Part H blocks use the same variable names and executable logic, the only remaining behavioural difference should be the explicit wall.Flip() call, which can then be tested independently before consolidating both implementations into a single shared repositioning engine.


## Commit Message

Refactor non-flipped Part H centreline offset selection


