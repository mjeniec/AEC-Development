# Sheets - Development Test Log

---

# Commit 003

---

## Git Commit #

003

---

## Commit Message

Apply viewport type and import office view template

---

## Change Made

Extended the CRiT: Sheets prototype to apply office-standard configuration to both the viewport and the planning view.

1) Viewport Type

The script now automatically changes the newly created viewport to the office-standard:

No Title

After creating the viewport, the script retrieves the valid viewport type IDs using:

viewport.GetValidTypes()

The valid types are iterated and their type names retrieved using the built-in Revit type-name parameter:

DB.BuiltInParameter.SYMBOL_NAME_PARAM

When the No Title viewport type is identified, its ElementId is stored and applied to the viewport using:

viewport.ChangeTypeId(no_title_type_id)

An exception is raised if the required viewport type cannot be found.

2) View Template

The script now automatically applies the office-standard planning view template:

CRiT - Planning - Floor Plan

The active project is first searched for the required template using a FilteredElementCollector of DB.View objects.

Because Revit view templates are also DB.View objects, the script identifies the required template using:

view.IsTemplate

and:

view.Name

If the template already exists in the active project, the existing template is used.

If the template does not exist, the script accesses the external office standards file:

CRiT_Office_Standards.rvt

The standards RVT is opened in the background using:

app.OpenDocumentFile()

The standards document is searched for the required planning view template.

The template's ElementId is added to a .NET List[DB.ElementId], as required by the Revit API CopyElements() method.

The view template is then copied from the standards document into the active project using:

DB.ElementTransformUtils.CopyElements()

with:

standards_doc as the source document;
the required template ElementId collection;
doc as the destination document;
DB.Transform.Identity as the transform;
a default DB.CopyPasteOptions() object.

CopyElements() returns the ElementId of the newly copied template in the active project.

The copied template is retrieved from the active document using:

doc.GetElement()

and stored as planning_template.

The external standards document is then closed without saving using:

standards_doc.Close(False)

Finally, the planning view is assigned the office-standard template using:

planning_view.ViewTemplateId = planning_template.Id


---

## Reason for Change

The previous CRiT: Sheets prototype successfully created and positioned a viewport but still relied on configuration already present in the active Revit project.

This change begins separating office standards from project-specific content.

The viewport type is now controlled programmatically, ensuring that drawings created by CRiT use the required No Title presentation rather than whichever viewport type Revit assigns by default.

More significantly, the script no longer requires the planning view template to already exist in the project.

An external Revit standards file has been introduced:

CRiT_Office_Standards.rvt

This acts as a source of native Revit office-standard elements.

The standards file currently contains:

CRiT - Planning - Floor Plan
CRiT - Construction - Floor Plan

The script follows the workflow:

Check active project → use existing template if available → otherwise retrieve from office standards → copy into project → assign to view

This establishes an important architectural principle for CRiT:

native Revit standards can be maintained in an external Revit standards file;
CRiT can determine which standards are required;
missing standards can be deployed automatically into individual projects.

This avoids requiring every project to be manually configured before CRiT can create office-standard drawings.

---


# Revit Test Results


## Viewport Type Assignment
[x]

Error / Notes:

Newly created viewport successfully changed to the No Title viewport type.

---

## Existing View Template
[x]

Error / Notes:

When CRiT - Planning - Floor Plan already exists in the active project, the existing template is identified and assigned successfully.


---

## Missing View Template Import
[x]

Error / Notes:

When CRiT - Planning - Floor Plan is removed from the active project, the script successfully:

- opens CRiT_Office_Standards.rvt;
- finds the required template;
- copies it into the active project;
- retrieves the copied template;
- assigns it to the planning view.

---

## Existing Sheet Workflow Regression
[x]

Error / Notes:

Sheet creation, calculated viewport placement and No Title viewport assignment continue to operate successfully after introducing the external standards workflow.


---


## Overall Result

The required office-standard planning view template can now be automatically applied whether or not it already exists in the active project.

If missing, CRiT retrieves the template from the external office standards RVT and copies it into the project before assignment.

Existing sheet creation and viewport placement functionality remains operational.

---

## Next Change / Hypothesis

The next change should remove the current dependency on the required planning view already existing in the project.

CRiT should check whether Proposed Ground Floor - Planning exists and, if it does not, create the required floor-plan view using the appropriate level and ViewFamilyType.

The newly created view can then follow the workflow established in this commit:

Create/Find View → Apply Office View Template → Create Sheet → Create Viewport

This will move CRiT closer to generating a drawing package from defined office standards rather than relying on manually prepared project views.



