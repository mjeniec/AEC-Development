# Brick Coordinator - Development Test Log

---

# Commit 002

---

## Git Commit #

002

---

## Commit Message

Refactor flipped Part F corner classification

---

## Change Made

Removed dependence on clockwise/anti-clockwise loop direction for the flipped engine's corner classification.

Corner type is now determined directly from the sign of the local cross product at each corner.

Current hypothesis:

- Selected exterior track always has wall core on the RIGHT.
- Therefore outside is on the LEFT of the selected track.
- Negative cross product (right turn) = external corner.
- Positive cross product (left turn) = internal corner.

(The old is_ccw calculation has been retained temporarily but is no longer used.)

---

## Reason for Change

The previous algorithm relied on determining whether an entire loop was clockwise or anti-clockwise.

After introducing user selection of the exterior track (Part D), either perimeter can now be selected, making whole-loop 
direction an unreliable way of identifying external corners.

This change tests whether corner classification can instead be based entirely on local geometry.

---

# Revit Test Results

## FLIPPED (Exterior on Left)

### Closed Loop - Clockwise
[x]

Error / Notes:

Corner classification correct.
All outside corners classified consistently.
Physical wall repositioning successful.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Corner classification correct.
All outside corners classified consistently.
Physical wall repositioning successful.

---

### Open Loop
[x]

Error / Notes:

Corner conditions correct.
Physical wall repositioning successful.

---

## NON-FLIPPED (Exterior on Right)

### Closed Loop - Clockwise
[ ]

Error / Notes:

Not yet tested.

---

### Closed Loop - Anti-clockwise
[ ]

Error / Notes:

Not yet tested.

---

### Open Loop
[ ]

Error / Notes:

Not yet tested.

---

## Overall Result

The flipped engine no longer depends on global loop direction for corner classification.

Testing suggests the local cross product alone is sufficient when combined with the selected exterior track.

---

## Next Change / Hypothesis

Refactor the non-flipped engine to use the same Part C–F architecture.

Test whether the same local corner-classification rule also applies to the non-flipped engine. If successful, remove the 
obsolete `is_ccw` logic entirely from both engines.


## Commit Message

Refactor flipped Part F to use local corner classification


