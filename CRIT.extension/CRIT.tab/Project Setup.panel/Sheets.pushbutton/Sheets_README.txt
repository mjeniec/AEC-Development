# CRiT: Sheets

**CRiT: Sheets** is a Revit drawing setup and issue-management tool intended to automate repetitive drawing-production tasks such as creating sheets, setting up views, applying view templates, populating title blocks, exporting drawing packages, and maintaining an issue register.

The aim is to encode an office's standard drawing setup so that a project drawing package can be created consistently and quickly while still allowing project-specific drawings and overrides where required.

---

## Core Concept: Drawing Definitions

Rather than storing only a list of standard drawing names, CRiT: Sheets will maintain an **office database of standard drawing definitions**.

SQLite is currently proposed for this database.

A drawing definition could contain information such as:

* Drawing title
* Drawing type / RIBA stage
* Revit view type
* Associated level (where applicable)
* View template
* Default scale
* Default sheet size
* Default sheet orientation
* Drawing number / numbering convention
* Other standard drawing properties

For example:

**Proposed Ground Floor Plan — Planning**

* Stage: Planning
* View Type: Floor Plan
* Level: Ground Floor
* View Template: Planning - Floor Plan
* Scale: 1:100
* Sheet Size: A1
* Orientation: Landscape
* Drawing Number: PL-100

The database therefore describes not simply **what drawings normally exist**, but **how those drawings should be configured**.

This allows CRiT: Sheets to translate a user's selection of a drawing into the Revit operations required to create it.

Project-specific drawings can still be created without adding them permanently to the office database.

---

# 1. New Project

### 1. Run `CRiT: Sheets → New Project`

Starts the initial drawing setup process for a new Revit project.

### 2. Enter project information

A dialogue asks the user to enter/select information such as:

* Project number
* Project name
* Project address
* Client
* Drawing stage / RIBA stage
* Other information required by the office title block

This project information should be stored so that it does not need to be entered again when additional drawings are created or issued later.

### 3. Select required drawings

CRiT displays the standard drawings available in the office drawing-definition database for the selected stage.

For example:

* Existing Site Plan
* Existing Ground Floor Plan
* Existing Elevations
* Proposed Site Plan
* Proposed Ground Floor Plan
* Proposed Roof Plan
* Proposed Elevations
* Proposed Sections

The user selects the drawings required for the project.

Each drawing already has default settings defined by the office database, including its typical:

* View type
* View template
* Scale
* Sheet size
* Sheet orientation

The user can override these defaults where necessary.

For the initial version of CRiT: Sheets, **sheet size and orientation will use office defaults with a user override**.

A future version could investigate automatically selecting an appropriate sheet size based on view scale, crop extents and available title-block area.

### 4. Automatically create drawing package

For each selected drawing, CRiT automatically:

* Creates or duplicates the required Revit view
* Names the view according to office standards
* Applies the appropriate view template
* Sets the required scale
* Creates the sheet
* Selects the appropriate title block
* Populates title-block/project information
* Places the view onto the sheet
* Applies the appropriate sheet/drawing numbering convention

The result should be a largely complete drawing package ready for project-specific adjustment and annotation.

---

# 2. Add Drawing

### 1. Run `CRiT: Sheets → Add Drawing`

Used when additional drawings are required after the initial project setup.

### 2. Select drawing stage/type

The user selects the relevant drawing stage, for example:

* Planning
* Tender
* Construction

Existing project information should already be stored in the Revit project and therefore should not need to be entered again.

### 3. Select drawing

CRiT displays relevant standard drawing definitions from the office database.

Ideally, drawings already created within the project are either hidden or clearly identified.

For example, the user could select:

* Proposed Section AA
* Proposed Section BB
* Proposed Roof Plan
* Construction Ground Floor Plan
* Wall Type Details

Default view template, scale, sheet size and other properties are retrieved from the drawing definition.

The user can override appropriate properties where required.

### 4. Create a project-specific drawing

If the required drawing does not exist in the office database, the user can select:

**Custom / Project-Specific Drawing**

For example:

> Timber Stair Detail

CRiT creates and configures the drawing using user-selected properties.

This drawing is stored within the project but **is not automatically added to the central office drawing-definition database**.

This keeps the office database controlled and prevents project-specific drawings gradually polluting the standard drawing library.

### 5. Automatically set up drawing

CRiT creates the required:

* View
* View configuration
* View template
* Sheet
* Title block
* Drawing number
* Viewport placement

The new drawing then becomes part of the project's drawing package.

---

# 3. Drawing Issue

### 1. Run `CRiT: Sheets → Drawing Issue`

Starts the drawing issue/export process.

### 2. Select drawings

CRiT displays the sheets currently available within the project.

The user selects the drawings to be issued.

The user also enters the required issue information, potentially including:

* Issue / revision
* Issue date
* Issue description/comment
* Issue purpose/status

### 3. Export drawing package

CRiT automatically exports the selected drawings to the appropriate project issue folder.

The exported package could follow a standard structure such as:

`Project → Drawing Issues → [Date]_[Issue]`

PDF filenames should follow the office drawing naming convention.

### 4. Update issue register

CRiT maintains a drawing issue register containing information such as:

* Drawing number
* Drawing title
* Revision
* Issue date
* Issue description/status

On the first issue, CRiT creates the register.

For subsequent issues, CRiT adds the new issue information to the existing register.

The register could initially be generated as an Excel file and automatically exported to PDF as part of the issue package.

---

# Initial Development Strategy

CRiT: Sheets will be developed by first understanding and reproducing the required workflow manually in Revit before attempting to automate it.

The initial test case will use the **Norfolk House** Revit project.

The first exercise will manually create two versions of the same drawing:

1. **Planning — Proposed Ground Floor Plan**
2. **Construction — Proposed Ground Floor Plan**

This will establish how the same model information is represented differently for different drawing purposes and provide practical experience with:

* Revit views
* View duplication
* Crop regions
* View scales
* Visibility / Graphics
* View templates
* Sheets
* Title block families and types
* Title-block parameters
* Viewports
* Drawing numbering
* Project information

Once this workflow is understood manually, the individual operations can progressively be reproduced using Python, pyRevit and the Revit API.

The initial development principle is therefore:

**Understand the Revit workflow → define the office standard → automate the standard → add project-specific flexibility.**

---

# Possible Future Development

Potential later features include:

* Automatic sheet-size selection based on view extents and scale
* Automatic viewport positioning and sheet layout
* Multiple views / schedules / legends per sheet
* Automatic drawing numbering
* Revision management
* Drawing package validation before issue
* Detection of missing or incorrectly configured drawings
* Comparison of the current project drawing set against the office standard
* Integration with wider CRiT project checking and project data



## Future: Multi-User / Enterprise Architecture

The initial version of CRiT: Sheets will use a simple local SQLite database and is primarily intended as a single-user prototype.

If CRiT were eventually deployed across a larger practice, the software architecture would need to consider multiple users accessing shared data simultaneously.

Topics to investigate in a future version include:

* **Concurrency** — handling multiple users reading or modifying shared data at the same time.
* **Transactions** — ensuring database operations either complete successfully or are safely rolled back.
* **Database architecture** — understanding when a local SQLite database should be replaced by a client/server database such as PostgreSQL.
* **API / server architecture** — potentially placing a CRiT server/API between Revit clients and the central database rather than allowing clients to access the database directly.
* **Permissions and authentication** — controlling who can read or modify office standards.
* **Performance and scalability** — ensuring the system remains responsive as the number of users and amount of data increases.
* **Failure handling** — dealing safely with interrupted operations, network failures and unavailable services.
* **Data versioning / synchronisation** — ensuring users are working with current office standards when central data changes.

These issues are **not requirements for the initial CRiT: Sheets prototype**. The first version should remain deliberately simple.

A useful future software-engineering exercise would be to ask:

> **How would CRiT need to change if it were deployed to 500 architects across multiple offices?**

This can be used later to explore database servers, APIs, concurrency, authentication, deployment and scalable application architecture using a system that is already understood.


