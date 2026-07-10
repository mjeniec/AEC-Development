# Brick Coordinator - Development Test Log

---

# Commit 006

---

## Git Commit #

006

---

## Commit Message

Refactor non-flipped Part H wall join management

---

## Change Made

Refactored the non-flipped engine's Part H to temporarily disable wall joins before repositioning and restore them after all walls have been moved.

Changes include:

- Added a preprocessing loop to disallow joins at both ends of every selected wall before repositioning begins.
- Left the existing wall repositioning algorithm unchanged.
- Added a post-processing loop to restore wall joins after all walls have been repositioned.
- Adopted the same wall join management sequence already used by the flipped engine.

---

## Reason for Change

The flipped engine temporarily disables wall joins while walls are being repositioned to prevent Revit from automatically modifying wall geometry during the movement process.

Introducing the same behaviour into the non-flipped engine reduces another architectural difference between the two Part H implementations without altering the centreline repositioning algorithm.

This continues the process of making both engines execute the same sequence of operations before unifying the remaining repositioning logic.

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

Wall joins restored correctly.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Wall repositioning successful.

Wall joins restored correctly.


---

### Open Loop
[x]

Error / Notes:

Wall repositioning successful.

Wall joins restored correctly.

---

## Overall Result

Introducing temporary wall join management does not alter the repositioning behaviour of the non-flipped engine for the tested scenarios.

The non-flipped engine now follows the same high-level repositioning workflow as the flipped engine by:

temporarily disabling wall joins;
repositioning all walls; and
restoring wall joins once repositioning is complete.

This removes another architectural difference between the two Part H implementations.

A separate pre-existing issue remains on some irregular closed-loop layouts, where corners may not reconnect perfectly after resizing. As this behaviour predates the current refactor and differs between the two engines, it has been deferred until both engines share identical repositioning logic.


---

## Next Change / Hypothesis

Replace the non-flipped engine's single-candidate centreline offset selection with the flipped engine's two-candidate centreline selection algorithm.

Once both engines determine the centreline offset using the same two-candidate comparison, the initial perpendicular direction should no longer influence the result, removing another substantive behavioural difference between the two Part H implementations.


## Commit Message

Refactor non-flipped Part H wall join management


