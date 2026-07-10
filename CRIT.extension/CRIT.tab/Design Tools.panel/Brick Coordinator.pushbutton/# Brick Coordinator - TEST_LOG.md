# Brick Coordinator - Development Test Log

---

# Commit 003

---

## Git Commit #

003

---

## Commit Message

Refactor non-flipped engine through Part E

---

## Change Made

Refactored the non-flipped engine to match the architecture of the flipped engine through Parts B–E.

Changes include:

- Unified geometry extraction.
- Common shape detection for open runs and closed loops.
- User confirmation of the exterior track for both layout types.
- Replacement of the original sorting engine with the new packaged track sorter.
- Removal of the old mirrored-track generation logic from Part E. 
- Added diagnostics comparing original Revit LocationCurve directions with the sorted exterior track.

No changes have yet been made to the executable Part F corner-classification logic in the non-flipped engine.

---

## Reason for Change

The long-term goal is for the flipped and non-flipped engines to use the same software architecture before duplicated logic is consolidated.

This commit establishes equivalent data structures and processing through Part E in both engines.

Both engines now pass the following data into Part F:

ordered_data
ordered

This allows Part F to be refactored incrementally while retaining a clear, testable baseline.

---

# Revit Test Results

## FLIPPED (Exterior on Left)

### Closed Loop - Clockwise
[x]

Error / Notes:

Sorted selected track runs opposite to the original Revit LocationCurve direction.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Sorted selected track runs opposite to the original Revit LocationCurve direction.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

### Open Loop
[x]

Error / Notes:

Sorted selected track runs opposite to the original Revit LocationCurve direction.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

## NON-FLIPPED (Exterior on Right)

### Closed Loop - Clockwise
[x]

Error / Notes:

Each sorted wall segment preserves its original Revit LocationCurve direction.

The sorted sequence may begin at a different wall, but this is only a rotation of the closed loop.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

### Closed Loop - Anti-clockwise
[ ]

Error / Notes:

Part F appears to allocate brick conditions and resize the selected exterior track, but physical wall repositioning fails.

Revit reports an error stating that the elements are reversed.

This is currently the only known failing test scenario.

The failure has not yet been investigated and should be preserved as the baseline for the next refactor stage.

---

### Open Loop
[x]

Error / Notes:

Each sorted wall segment preserves its original Revit LocationCurve direction.

Brick-condition assignment correct.

Physical wall repositioning successful.

---

## Overall Result

The non-flipped engine has been successfully refactored to match the flipped engine through Part E.

Five of the six principal test scenarios currently complete successfully:

Flipped open run
Flipped clockwise closed loop
Flipped anti-clockwise closed loop
Non-flipped open run
Non-flipped clockwise closed loop

The remaining failure is:

Non-flipped anti-clockwise closed loop

This scenario reaches the physical wall-repositioning stage but fails with a Revit error indicating that elements are reversed.

Diagnostics otherwise support the following shared geometric invariant:

Outside lies on the LEFT of the selected sorted exterior track.
Wall core lies on the RIGHT of the selected sorted exterior track.

The failing anti-clockwise scenario may therefore relate to downstream wall orientation or LocationCurve replacement rather than the selection and sorting architecture itself. This remains a hypothesis and has not yet been proven.

---

## Next Change / Hypothesis

Refactor Part F of the non-flipped engine to replace the legacy global is_ccw logic with the same local corner-classification rule used successfully by the flipped engine.

Test all six scenarios again after that single logical change.

Particular attention should be given to the non-flipped anti-clockwise closed loop to determine whether:

- the local Part F classification resolves the reversed-elements error, or
- the error originates later in Part H during physical wall repositioning.

Do not remove any additional logic until this has been tested.


## Commit Message

Refactor non-flipped engine Parts B-E to match flipped engine


