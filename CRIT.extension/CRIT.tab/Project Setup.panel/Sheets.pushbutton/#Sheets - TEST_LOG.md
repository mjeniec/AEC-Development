# Sheets - Development Test Log

---

# Commit 002

---

## Git Commit #

002

---

## Commit Message

Centre viewport within usable sheet area

---

## Change Made

Replaced the temporary hard-coded viewport placement coordinate with a calculated placement point based on the dimensions of the newly created sheet.

The script now retrieves the sheet bounds using:

`sheet.Outline`

This returns a Revit `BoundingBoxUV` representing the physical extents of the sheet in paper space.

The minimum and maximum sheet coordinates are retrieved using:

- `Min.U`
- `Max.U`
- `Min.V`
- `Max.V`

The script then calculates the centre of the sheet rather than relying on an arbitrary `XYZ` coordinate.

Initial testing showed that centring the viewport on the entire physical sheet positioned the drawing too low because the calculation 
included the title strip at the bottom of the A3 title block.

A 40 mm title-strip height was therefore introduced:

`A3_title_strip_height_mm = 40`

The value is converted from millimetres to Revit's internal units using:

`DB.UnitUtils.ConvertToInternalUnits()`

The bottom of the usable drawing region is then calculated as:

`usable_v_min = v_min + A3_title_strip_height`

The centre of the usable drawing area is calculated using:

`u_centre = (u_min + u_max) / 2`

`v_centre = (usable_v_min + v_max) / 2`

These coordinates are used to construct the `XYZ` placement point supplied to `Viewport.Create()`.

The viewport is therefore now positioned automatically relative to the dimensions of the selected sheet rather than using a fixed coordinate.


---

## Reason for Change

Commit 001 demonstrated that an existing Revit view could successfully be placed onto a newly created sheet, but used the temporary placement point:

`XYZ(1, 1, 0)`

This caused the viewport to be positioned incorrectly because the coordinate had no relationship to the actual sheet dimensions.

The purpose of this change was to understand Revit's sheet-space coordinate system and develop the first calculated viewport placement behaviour.

Using `ViewSheet.Outline` allows the script to determine the physical sheet dimensions dynamically.

This means the placement calculation is based on the actual sheet extents rather than hard-coded A3 width and height values.

Testing also demonstrated an important distinction between:

- the physical centre of the sheet;
- the centre of the usable drawing area.

Because the title strip occupies approximately 40 mm at the bottom of the current A3 title block, the usable drawing region has a different vertical 
centre from the complete sheet.

The updated calculation accounts for this reserved area and positions the viewport more appropriately.

This establishes the beginnings of a sheet-layout system in which CRiT can position drawings according to defined usable regions rather than arbitrary coordinates.

---

---

# Revit Test Results


## Sheet Outline Retrieval
[x]

Error / Notes:

The newly created `ViewSheet` successfully returns its paper-space bounds using:

`sheet.Outline`

For the A3 landscape title block, the returned values were approximately:

`u_min = 0.0092 ft`

`u_max = 1.3871 ft`

`v_min = -0.0066 ft`

`v_max = 0.9678 ft`

The resulting width and height correspond approximately to the expected A3 landscape dimensions of 420 × 297 mm.

---

## Physical Sheet Centre Calculation
[x]

Error / Notes:

The horizontal and vertical centre coordinates of the complete sheet were successfully calculated from the minimum and maximum UV coordinates.

The viewport was successfully placed using the resulting calculated `XYZ` point.

Testing confirmed that the viewport was centred relative to the complete physical sheet.

However, the resulting drawing position was visually too low because the calculation included the title strip at the bottom of the sheet.


---

## Title Strip Allowance
[x]

Error / Notes:

The A3 title strip was measured at approximately 40 mm.

The script now stores this as:

`A3_title_strip_height_mm = 40`

The dimension is converted to Revit internal units using `UnitUtils.ConvertToInternalUnits()` before being used in sheet-space calculations.

---

## Usable Drawing Area Calculation
[x]

Error / Notes:

The lower boundary of the usable drawing region is successfully calculated by adding the title-strip height to the minimum V coordinate.

The horizontal centre remains based on the complete sheet width because the current title strip extends horizontally across the bottom of the sheet.

The vertical centre is calculated between the top of the title strip and the maximum V coordinate.

---

## Viewport Position
[x]

Error / Notes:

The viewport is successfully placed approximately centrally within the usable drawing area.

The previous arbitrary placement point:

`XYZ(1, 1, 0)`

has been removed.

Viewport placement is now calculated from the actual sheet dimensions and the reserved title-strip area.

---


## Overall Result

Viewport placement is now calculated dynamically rather than using an arbitrary hard-coded coordinate.

The script successfully:

- retrieves the physical bounds of the newly created sheet;
- reads the minimum and maximum U/V coordinates;
- calculates the sheet centre;
- accounts for the 40 mm title strip;
- defines a reduced usable drawing region;
- calculates the centre of that usable region;
- converts the calculated U/V position into an `XYZ` point;
- places the viewport at the calculated position.

Testing also confirmed that `ViewSheet.Outline` dimensions change according to the physical sheet and therefore provide a basis for supporting different sheet sizes without hard-coding their overall dimensions.

The current implementation still contains an A3-specific hard-coded title-strip height. This is acceptable for the current prototype but will eventually need to become part of a more general sheet-layout definition.

---

## Next Change / Hypothesis

The next change should begin controlling the appearance and configuration of the viewport rather than its position.

The immediate next step is to investigate viewport types and programmatically assign the required office-standard viewport type, such as:

`No Title`

This will introduce another important Revit object relationship:

`Viewport → Viewport Type`

Further development can then investigate:

- viewport title configuration;
- view scale;
- view-template assignment;
- crop configuration;
- creation of missing views;
- support for different sheet sizes;
- storing sheet-specific usable regions and title-strip dimensions as configuration data rather than hard-coded Python values.

The longer-term objective is for CRiT to understand both the drawing definition and the sheet-layout definition required to create a consistent office-standard drawing package automatically.



