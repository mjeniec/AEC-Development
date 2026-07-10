# Brick Coordinator - Development Test Log

---

# Commit 005

---

## Git Commit #

005

---

## Commit Message

Refactor non-flipped Part H LocationCurve validation

---

## Change Made

Refactored the non-flipped engine's Part H so that the wall Location is retrieved and validated before any repositioning calculations are performed.

Changes include:

- Moved retrieval of wall.Location to the beginning of the repositioning loop.
- Validated that wall.Location is a LocationCurve immediately after retrieving it.
- Removed the later nested isinstance(wall_loc, LocationCurve) check.
- Left all centreline-offset calculations, repositioning logic and wall movement unchanged.

---

## Reason for Change

The flipped engine validates the wall's LocationCurve before performing any repositioning calculations.

This change brings the non-flipped engine into the same architectural structure, allowing the remainder of Part H to assume that a valid LocationCurve exists.

The intention is to make the control flow of both engines identical before refactoring the remaining behavioural differences.

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

Wall repositioning unchanged.

No behavioural differences observed.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Wall repositioning unchanged.

No behavioural differences observed.

---

### Open Loop
[x]

Error / Notes:

Wall repositioning unchanged.

No behavioural differences observed.

---

## Overall Result

Moving the LocationCurve validation to the beginning of the repositioning loop does not change behaviour.

The non-flipped engine now follows the same execution structure as the flipped engine by validating the wall location before entering the repositioning calculations.

This reduces one architectural difference between the two Part H implementations without altering the repositioning algorithm.

---

## Next Change / Hypothesis

Introduce temporary wall join management into the non-flipped engine by:

- disallowing joins before repositioning; and
- restoring joins after repositioning.

This behaviour already exists in the flipped engine and should be independent of the centreline repositioning calculations.


## Commit Message

Refactor non-flipped Part H LocationCurve validation


