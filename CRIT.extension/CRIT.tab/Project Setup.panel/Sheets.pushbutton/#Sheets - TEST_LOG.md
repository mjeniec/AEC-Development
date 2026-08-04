# Sheets - Development Test Log

---

# Commit 001

---

## Git Commit #

001

---

## Commit Message

Create test sheet and place existing planning view

---

## Change Made

Created the first working pyRevit prototype for CRiT: Sheets.

The script currently:

- retrieves the active Revit document;
- collects loaded title block types using `FilteredElementCollector`;
- filters the title block collection to identify the `Title_Blocks_A3_Metric` family;
- stores the matching title block `FamilySymbol` for use when creating a sheet;
- collects Revit `View` objects from the current document;
- searches for the existing view named `Proposed Ground Floor - Planning`;
- creates a new `ViewSheet` using the selected A3 title block type;
- assigns the sheet number `HIW-UPB-ZZ-00-DR-A-0999`;
- assigns the sheet name `CRiT Test Sheet`;
- creates a `Viewport`;
- places the existing planning view onto the newly created sheet using an initial test `XYZ` placement point.

The Revit modifications are carried out inside a pyRevit transaction using:

`with revit.Transaction("Create CRiT Sheet")`

This provides the first complete proof-of-concept for automatically creating a sheet and placing an existing view onto it.


---

## Reason for Change

The purpose of this first commit is to establish the minimum working Revit API workflow required by CRiT: Sheets.

Before developing drawing databases, interfaces, automatic view creation or issue-management functionality, the tool first needs to prove that it can programmatically reproduce the basic manual drawing setup process.

This commit establishes the relationship between the principal Revit objects involved:

- `FamilySymbol` — the title block type used when creating the sheet;
- `View` — the existing documentation view to be placed;
- `ViewSheet` — the sheet created by the script;
- `Viewport` — the object that places the view onto the sheet.

The commit also provides practical experience using:

- `FilteredElementCollector`;
- category and class filtering;
- Revit element IDs;
- Revit API classes and properties;
- pyRevit transaction context managers;
- `Viewport.Create()`;
- `XYZ` placement coordinates.

This forms the basic API foundation from which the wider CRiT: Sheets workflow can be developed.

---

# Revit Test Results

## FLIPPED (Exterior on Left)

## Title Block Collection
[x]

Error / Notes:

The script successfully collects loaded title block types and identifies the `Title_Blocks_A3_Metric` family.

The returned title block type is a Revit `FamilySymbol`.

---

## Planning View Collection
[x]

Error / Notes:

The script successfully collects Revit `View` objects and identifies the existing view:

`Proposed Ground Floor - Planning`

---

## Sheet Creation
[x]

Error / Notes:

A new sheet is successfully created using the A3 metric title block.

Sheet number:

`HIW-UPB-ZZ-00-DR-A-0999`

Sheet name:

`CRiT Test Sheet`

---

## Viewport Creation
[x]

Error / Notes:

The existing `Proposed Ground Floor - Planning` view is successfully placed onto the newly created sheet.

The view had to be removed from its previous sheet before testing because a standard Revit plan view cannot normally be placed on multiple sheets simultaneously.

---

## Viewport Position
[ ]

Error / Notes:

The viewport is currently placed using the temporary test coordinate:

`XYZ(1, 1, 0)`

The view is therefore successfully created on the sheet but is not positioned correctly within the usable drawing area.

Automatic or calculated viewport positioning remains to be implemented.

---


## Overall Result

The first CRiT: Sheets prototype successfully reproduces the basic Revit workflow of:

- selecting a title block type;
- identifying an existing view;
- creating a new sheet;
- assigning sheet metadata;
- creating a viewport;
- placing the view onto the sheet.

The core object relationship has now been demonstrated successfully:

`View → Viewport → ViewSheet`

with the title block `FamilySymbol` used during sheet creation.

The current implementation is deliberately hard-coded and intended only as a proof-of-concept.

The main outstanding issue is viewport positioning, which currently uses an arbitrary `XYZ` coordinate and causes the placed view to extend beyond the usable sheet area.


---

## Next Change / Hypothesis

The next change should focus on viewport placement.

Rather than using a hard-coded coordinate, the script should investigate how to determine an appropriate placement point based on the sheet and title block geometry.

The immediate objective is to understand:

- the sheet coordinate system;
- the meaning of `XYZ` coordinates in sheet space;
- the usable drawing area of the selected title block;
- how viewport bounds can be measured;
- how a viewport can be positioned centrally or according to a defined office layout.

Once viewport positioning is understood, the next stages can begin to introduce:

- creation of missing views;
- assignment of view templates;
- drawing scale;
- viewport type;
- sheet size selection;
- drawing definitions;
- project information;
- eventual SQLite-backed drawing standards.

The development approach should remain incremental, with each new Revit object or behaviour tested independently before expanding the workflow.



