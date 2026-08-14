from pyrevit import revit, DB
from System.Collections.Generic import List

doc = revit.doc 

A3_title_strip_height_mm = 40
A3_title_strip_height = DB.UnitUtils.ConvertToInternalUnits(A3_title_strip_height_mm, DB.UnitTypeId.Millimeters)


# 1. Find the correct TITLEBLOCK

titleblock_type = None

collector = DB.FilteredElementCollector(doc) \
    .OfCategory(DB.BuiltInCategory.OST_TitleBlocks) \
    .WhereElementIsElementType()

for tb_type in collector:
    if tb_type.Family.Name == 'Title_Blocks_A3_Metric':
        titleblock_type = tb_type # stores the actual FamilySymbol object (not just the name)
        break

if titleblock_type is None:
    raise Exception("A3 Metric Titleblock Type Not Found")

# heirachy: 0ST_TitleBlocks (Category): A3 Metric Titleblock (Family): Standard (Type)


# 2. Find the correct VIEW

planning_view = None

view_collector = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()

for view in view_collector:
    if view.Name == 'Proposed Ground Floor - Planning':
        planning_view = view
        break

if planning_view is None:
    raise Exception("Planning View Not Found")


# 3. Find the correct VIEW TEMPLATE
# Note: Views and View Templates are all DB.View objects

planning_template = None 

view_template_collector = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()

for view in view_template_collector:
    if view.IsTemplate and view.Name == 'CRiT - Planning - Floor Plan':
        planning_template = view
        break


if planning_template is None:

    standards_path = r"D:\WORK\AEC TECH\AEC Development\CRiT.extension\Standards\CRiT_Office_Standards.rvt"
    app = doc.Application 
    standards_doc = app.OpenDocumentFile(standards_path)

    standards_planning_template = None
    standards_view_template_collector = DB.FilteredElementCollector(standards_doc).OfClass(DB.View).ToElements()

    for view in standards_view_template_collector:
        if view.IsTemplate and view.Name == 'CRiT - Planning - Floor Plan':
            standards_planning_template = view 
            break   

    if standards_planning_template is None:
        raise Exception("Standards Planning Template Not Found")       
           
    template_ids = List[DB.ElementId]()
    template_ids.Add(standards_planning_template.Id)

    transform = DB.Transform.Identity
    copy_options = DB.CopyPasteOptions()

    with revit.Transaction("Import Planning View Template"):
        copied_ids = DB.ElementTransformUtils.CopyElements(
            standards_doc,
            template_ids,
            doc,
            transform, 
            copy_options        
        )

    standards_doc.Close(False)

    copied_template_id = list(copied_ids)[0]
    planning_template = doc.GetElement(copied_template_id)




with revit.Transaction("Create CRiT Sheet"):

    # 1. Assign VIEW TEMPLATE

    planning_view.ViewTemplateId = planning_template.Id


    # 2. Create SHEET

    sheet = DB.ViewSheet.Create(doc, titleblock_type.Id)
    sheet.SheetNumber = "HIW-UPB-ZZ-00-DR-A-0999"
    sheet.Name = 'CRiT Test Sheet'

    sheet_bounding_box = sheet.Outline

    u_min = sheet_bounding_box.Min.U
    u_max = sheet_bounding_box.Max.U
    v_min = sheet_bounding_box.Min.V
    v_max = sheet_bounding_box.Max.V

    usable_v_min = v_min + A3_title_strip_height

    u_centre = (u_min + u_max) / 2
    v_centre = (usable_v_min + v_max) / 2

    placement_point = DB.XYZ(u_centre,v_centre, 0)


    # 3. Create VIEWPORT
    
    viewport = DB.Viewport.Create(
        doc, 
        sheet.Id, 
        planning_view.Id, 
        placement_point
    )

    no_title_type_id = None

    for type_id in viewport.GetValidTypes():
        viewport_type = doc.GetElement(type_id)

        type_name = viewport_type.get_Parameter(
            DB.BuiltInParameter.SYMBOL_NAME_PARAM
        ).AsString()

        if type_name == "No Title":
            no_title_type_id = type_id
            break

    if no_title_type_id is None:
        raise Exception("No Title viewport type not found")

    viewport.ChangeTypeId(no_title_type_id)


  
                
        



