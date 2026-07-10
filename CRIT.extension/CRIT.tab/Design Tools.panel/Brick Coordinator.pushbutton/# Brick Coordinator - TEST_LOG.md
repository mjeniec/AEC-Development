# Brick Coordinator - Development Test Log

---

# Commit 008

---

## Git Commit #

008

---

## Commit Message

Refactor non-flipped Part H perpendicular vector initialisation 

---

## Change Made

Refactored the non-flipped engine's Part H so that both the geometry terminology and initial perpendicular vector calculation now match the flipped engine.

Changes include:

- Renamed the remaining Part H geometry variables to match the flipped engine:
- pt_start_ext → pt_start_track
- pt_end_ext → pt_end_track
- dir_vector → track_dir
- perpend_normal → perpend_vector
- Replaced the non-flipped perpendicular vector calculation with the equivalent expression used by the flipped engine.
- The initial perpendicular vector now points in the same direction in both engines.
- The previously introduced two-candidate centreline selection algorithm was retained unchanged.
- No other repositioning calculations were modified

---

## Reason for Change

Following the previous refactor, both engines determine the correct centreline by explicitly comparing both possible offset directions.

This means the initial perpendicular direction should no longer influence the final result.

Aligning both the geometry terminology and the initial perpendicular vector calculation removes another architectural difference between the two Part H implementations and confirms that the two-candidate centreline selection algorithm is independent of the initial vector orientation.

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

One intermittent corner overlap was observed during testing.

Although insufficient evidence exists to establish a pattern, the overlap appeared to occur more frequently on layouts drawn in a clockwise direction. Further investigation is required before drawing any conclusions.

No evidence suggests that changing the initial perpendicular vector introduced or increased the occurrence of the issue.

---

## Overall Result

Changing the initial perpendicular vector to match the flipped engine, together with adopting the same geometry variable naming, produced no observable behavioural changes in the standard non-flipped test scenarios.

This confirms the hypothesis that, once both candidate centreline positions are evaluated explicitly, the initial perpendicular direction no longer affects the final centreline selected.

The two Part H implementations now use the same geometry terminology and effectively identical repositioning logic, with the only remaining executable behavioural difference being the explicit wall.Flip() call in the flipped engine.

---

## Next Change / Hypothesis

Investigate the remaining behavioural difference between the two Part H implementations by testing the necessity of the explicit wall.Flip() call in the flipped engine.

Determine whether this operation is still required now that both engines use the same repositioning logic, or whether it can be removed while preserving the correct wall orientation for all flipped-wall scenarios.


## Commit Message

Refactor non-flipped Part H perpendicular vector initialisation


