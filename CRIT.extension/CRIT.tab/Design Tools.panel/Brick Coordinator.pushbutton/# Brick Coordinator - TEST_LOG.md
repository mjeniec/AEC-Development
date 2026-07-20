# Brick Coordinator - Development Test Log

---

# Commit 016

---

## Git Commit #

017

---

## Commit Message

Remove duplicate ordered edge representation

---

## Change Made

Simplified the data flow between Parts E and F by removing the redundant ordered list.

Previously Part E produced two parallel representations of the same ordered wall-track data:

- ordered_data — a list of dictionaries containing the matched Revit Wall element together with each edge's Start and End points.
- ordered — a second list containing only (Start, End) tuples extracted from ordered_data.

Part F has been updated to operate directly on ordered_data throughout.

The following changes were made:

- removed creation of the intermediate ordered list;
- updated edge count calculations to use ordered_data;
- updated first and last point retrieval to reference the Start and End values stored within ordered_data;
- updated current, previous and next edge access to use dictionary values rather than tuple indexing;
- updated cross-product calculations to reference the Start and End values directly from each edge dictionary;
- preserved the existing brick-condition algorithm and corner-classification logic;
- retained identical outputs by continuing to build the same EDGES data structure for Part G.

No functional behaviour was intentionally changed.

---

## Reason for Change

The ordered list duplicated information already contained within ordered_data.

Maintaining both structures created two parallel representations of the same ordered geometry which always had to remain synchronised.

Removing the duplicate representation simplifies the architecture by establishing ordered_data as the single source of truth for ordered wall-track information throughout Part F.

The updated implementation is also more self-documenting, as edge geometry is now accessed through descriptive dictionary keys such as:

edge["Start"]
edge["End"]
edge["Wall"]

rather than tuple index positions.

This reduces unnecessary data transformation while improving readability and maintainability.

---

# Revit Test Results

## FLIPPED (Exterior on Left)

### Closed Loop - Clockwise
[x]

Error / Notes:

Wall repositioning successful.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Wall repositioning successful.

---

### Open Loop
[x]

Error / Notes:

Wall repositioning successful.

---

## NON-FLIPPED (Exterior on Right)

### Closed Loop - Clockwise
[x]

Error / Notes:

Wall repositioning successful.

---

### Closed Loop - Anti-clockwise
[x]

Error / Notes:

Wall repositioning successful.

---

### Open Loop
[x]

Error / Notes:

Wall repositioning successful.

---


## Overall Result

Removing the intermediate ordered collection produced no behavioural changes.

All six standard regression tests continue to pass, confirming that:

- ordered wall-track geometry is still processed correctly;
- corner classification remains unchanged;
- brick-condition assignment remains unchanged;
- brick resizing remains unchanged;
- physical wall repositioning remains unchanged.

Part F now operates from a single ordered data structure:

ordered_data

rather than maintaining two parallel representations of the same geometry.

This establishes a cleaner architectural boundary between Parts E and F and prepares Part F for extraction into a dedicated helper function.

---

## Next Change / Hypothesis

Extract Part F into a dedicated helper function while preserving its existing algorithm.

The proposed function contract is:

def classify_brick_conditions(
    ordered_data,
    is_closed_loop_layout
):
    return EDGES

The initial extraction should preserve the current implementation without modifying the internal algorithm.

Potential internal helper functions (such as cross-product calculation or corner-condition determination) should be evaluated only after the high-level Part F extraction has been completed and verified against the existing regression tests.




