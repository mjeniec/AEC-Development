from pyrevit import revit, DB

doc = revit.doc 

A3_title_strip_height_mm = 40
A3_title_strip_height = DB.UnitUtils.ConvertToInternalUnits(A3_title_strip_height_mm, DB.UnitTypeId.Millimeters)




# Find the A3 metric title block type
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

# Find the correct view 

planning_view = None

view_collector = DB.FilteredElementCollector(doc).OfClass(DB.View).ToElements()

for view in view_collector:
    if view.Name == 'Proposed Ground Floor - Planning':
        planning_view = view
        break

if planning_view is None:
    raise Exception("Planning View Not Found")


with revit.Transaction("Create CRiT Sheet"):
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

    placement_point = DB.XYZ(u_centre,v_centre,0)

    viewport = DB.Viewport.Create(
        doc, sheet.Id, 
        planning_view.Id, 
        placement_point
    )


