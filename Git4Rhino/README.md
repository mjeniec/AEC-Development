# Git4Rhino

**Git4Rhino** is an experimental version-control system for Rhino intended to investigate whether software-development concepts such as commits, version history, branches, comparison and merging can be applied to architectural and computational design workflows.

The project is motivated by a common problem in architectural design: design development is often recorded through large numbers of manually saved files with names such as:

House_01.3dm
House_02.3dm
House_02_OptionA.3dm
House_02_OptionB.3dm
House_02_OptionB_Revised.3dm
House_03.3dm

These filenames attempt to record both the history of a project and the different design directions explored during that history.

Git4Rhino will investigate whether this process can instead be represented as structured version history.

For example:

                    Option A
                   /
Commit A → Commit B → Commit C
                   \
                    Option B

The initial project is intended as a proof of concept rather than a production-ready replacement for existing file-management or collaboration systems.

---

# Core Concept: Model Snapshots

Rather than treating each Rhino `.3dm` file as an independent version of a project, Git4Rhino will investigate storing structured **snapshots of the Rhino model**.

Using RhinoCommon, the tool could inspect Rhino objects and record information such as:

* Object GUID
* Object type
* Layer
* Geometry
* Object attributes
* Transform / position
* Other relevant object properties

A snapshot therefore represents the state of the model at a particular point in its development.

For example:

**Commit 004 — Test revised roof geometry**

* 3 objects added
* 1 object deleted
* 5 objects modified
* Roof Brep geometry changed
* Two structural curves repositioned

The aim is to move from file-level versioning:

> `House_OptionB_Revised_03.3dm`

towards model-aware versioning:

> **Commit 004 — Revise roof geometry**

---

# 1. Create Commit

### 1. Run `Git4Rhino → Commit`

The user records the current state of the Rhino model.

### 2. Enter commit message

The user enters a short description of the design change.

For example:

> Revise roof geometry

or:

> Test alternative stair position

### 3. Capture model state

Git4Rhino reads the relevant objects from the current Rhino document using RhinoCommon.

For each supported object, the system records sufficient information to identify the object and determine whether it has changed between model versions.

### 4. Store snapshot

The snapshot is stored as part of the project's version history.

The initial prototype could investigate using SQLite and/or serialized model data for storage.

The result is a chronological history such as:

Commit 001 — Initial massing
Commit 002 — Add courtyard
Commit 003 — Revise entrance
Commit 004 — Revise roof geometry

---

# 2. Version History

### 1. Run `Git4Rhino → History`

Displays the recorded development history of the current Rhino project.

Each commit should show information such as:

* Commit number / ID
* Date and time
* Commit message
* Number of objects added
* Number of objects deleted
* Number of objects modified

### 2. Select historic version

The user selects an earlier commit.

Git4Rhino displays information about the model at that point without immediately changing the current Rhino model.

The user should be able to investigate:

* What objects existed
* What objects were added
* What objects were deleted
* What objects changed
* What layers or properties changed

---

# 3. Compare Versions

### 1. Select two commits

The user selects two points in the model history.

For example:

Commit 004 — Initial roof geometry

and:

Commit 007 — Revised roof geometry

### 2. Calculate model differences

Git4Rhino compares the stored model states.

The comparison could classify objects as:

* Added
* Deleted
* Unchanged
* Modified

For modified objects, later versions could provide more detailed information such as:

* Geometry changed
* Position changed
* Layer changed
* Attributes changed

### 3. Visualise differences

A future interface could display the differences directly within Rhino.

For example:

* Added geometry highlighted
* Deleted geometry shown from the historic snapshot
* Modified geometry compared between versions
* Unchanged geometry visually subdued

The objective is to create a model-aware equivalent of a Git code diff.

---

# 4. Branches

One of the main areas Git4Rhino will investigate is applying the concept of **branches** to design development.

Architectural design frequently develops through alternative options.

For example:

                         Courtyard Option
                        /
Main Design → Commit 004
                        \
                         Linear Option

Instead of creating separate files for each option, Git4Rhino could allow the user to create named branches.

### Example

At Commit 004, the user creates:

* `courtyard-option`
* `linear-option`

Both initially represent the same model state.

The designer can then continue developing each option independently.

The history might become:

                    C05 → C06 → C07
                   /               courtyard-option
Commit 004
                   \
                    C05 → C06
                               linear-option

Switching branches would restore the Rhino model state associated with the selected branch.

This would allow alternative design directions to remain explicitly connected to the common design state from which they originated.

---

# 5. Switching Versions / Branches

The user should be able to move between recorded model states.

For example:

`main`

may contain the current agreed design, while:

`roof-study`

contains experimental roof geometry.

Switching to `roof-study` would reconstruct the model state associated with that branch.

Switching back to `main` would restore the agreed model state.

The initial prototype should investigate how this can be achieved safely without requiring the user to manually maintain multiple `.3dm` files.

---

# 6. Merge — Future Investigation

A later stage of Git4Rhino could investigate whether changes developed independently on different branches can be combined.

For example:

                        Branch A
                        Move staircase
                       /
Base Model
                       \
                        Branch B
                        Revise roof

If the changes affect independent objects, Git4Rhino could potentially produce a merged model containing both:

* the revised staircase position; and
* the revised roof.

This would represent a model-aware equivalent of a Git merge.

Automatic merging is **not a requirement for the initial proof of concept**.

---

# 7. Merge Conflicts — Future Investigation

The more difficult problem occurs when two branches modify the same object.

For example:

**Branch A**

Wall / surface object 123:
Moved 500 mm east

**Branch B**

Wall / surface object 123:
Geometry modified

Git4Rhino would need to recognise that both branches have independently changed the same object.

Rather than attempting an unsafe automatic merge, the system could identify this as a conflict.

A future interface could allow the designer to:

* Keep Branch A
* Keep Branch B
* Keep both objects
* Resolve the geometry manually

This would investigate whether software-development concepts of merge conflicts can be meaningfully translated into geometric design workflows.

---

# Initial Development Strategy

Git4Rhino should initially be developed as a deliberately limited proof of concept.

The first objective is **not** to build a complete version-control system for every type of Rhino object.

The first prototype should establish whether the core concept works.

Initial supported geometry could be limited to simple Rhino objects such as:

* Points
* Lines / curves
* Basic Breps

The first development stages could be:

1. Read objects from the active Rhino document using RhinoCommon.
2. Extract object GUIDs, geometry and basic attributes.
3. Convert this information into a serializable representation.
4. Store a model snapshot.
5. Modify the Rhino model.
6. Store another snapshot.
7. Compare the two snapshots.
8. Correctly identify added, deleted and modified objects.
9. Display the version history.
10. Introduce simple branches and switching between model states.

The initial development principle is therefore:

**Understand Rhino object data → capture model state → compare model states → build version history → introduce branching.**

Only once these fundamentals work should geometric merging be investigated.

---

# Initial Proof of Concept

A simple test model could contain:

* Several curves
* Several simple Breps
* Objects distributed across different layers

### Commit 001

Create initial geometry.

### Commit 002

* Move one object
* Delete one object
* Add one object
* Modify one object's geometry

Git4Rhino should correctly report:

* Added: 1
* Deleted: 1
* Modified: 2

The next test could create a branch from Commit 001.

### `option-a`

Move one group of objects.

### `option-b`

Modify a different group of objects.

Git4Rhino should preserve both development histories and allow the user to switch between them.

This would establish the core proof of concept before attempting more complex design models.

---

# Possible Future Development

Potential later features include:

* Visual model diffing inside the Rhino viewport
* Object-level version history
* Branch creation and management
* Branch visualisation
* Restore individual objects from historic commits
* Restore complete model states
* Automatic merging of independent object changes
* Merge-conflict detection
* Interactive geometric conflict resolution
* Commit tags / milestones
* Design-option comparison
* Commit notes and design rationale
* User attribution
* Multi-user workflows
* Grasshopper integration
* Remote repositories
* Cloud-hosted model history
* Integration with existing Git repositories
* Integration with wider AEC data platforms

---

# Technical Areas to Investigate

Git4Rhino is also intended as a software-engineering learning project.

Development will require investigation of:

* **RhinoCommon** — reading and manipulating Rhino model objects.
* **Object identity** — understanding how Rhino GUIDs behave as geometry is edited, replaced, copied or deleted.
* **Serialization** — converting Rhino geometry and attributes into data that can be stored and reconstructed.
* **Hashing** — efficiently determining whether stored model objects have changed.
* **Data storage** — investigating SQLite, files and other approaches to storing model history.
* **Snapshot architecture** — representing complete model states efficiently.
* **Diff algorithms** — determining differences between model states.
* **Branching** — representing alternative histories derived from a common model state.
* **State reconstruction** — rebuilding a Rhino model from a historic snapshot.
* **Conflict detection** — identifying objects independently modified on multiple branches.
* **Software architecture** — separating Rhino interaction, model representation, storage, comparison and UI concerns.
* **Testing** — developing repeatable tests for model-state and version-control behaviour.

---

# Longer-Term Question

The initial project is deliberately exploratory.

The broader question Git4Rhino is intended to investigate is:

> **What would version control look like if architectural design models were treated more like software repositories than collections of sequential files?**

Architects already create informal versions, branches and design options through duplicated files and naming conventions.

Git4Rhino will investigate whether these relationships can instead become explicit, queryable and structured parts of the design model's history.