from pyrevit import revit, DB

doc =  revit.doc 

phase = list(doc.Phases)[-1] # make more robust - just takes last item which will generally be New

# HELPER FUNCTIONS #

def get_exterior_facing(element, phase):

    bounding_box = element.get_BoundingBox(None)
    centre = (bounding_box.Min + bounding_box.Max) * 0.5 
    offset = DB.UnitUtils.ConvertToInternalUnits(0.5, DB.UnitTypeId.Meters)

    facing = element.FacingOrientation.Normalize()

   

    point_1 = centre + facing * offset
    point_2 = centre - facing * offset

    room_1 = doc.GetRoomAtPoint(point_1, phase)
    room_2 = doc.GetRoomAtPoint(point_2, phase)

# END FUNCTION HERE AND RETURN ROOM_1 + ROOM_2

    if room_1 is not None and room_2 is None:
        return facing * -1.0
    
    elif room_2 is not None and room_1 is None:
        return facing
    
    else:
        return None



def get_orientation(vector):

    x = vector.X
    y = vector.Y

    if abs(y) >= abs(x):

        if y >= 0:
            return 'North'
        else:
            return 'South'

    else:

        if x >= 0:
            return 'East'
        else:
            return 'West'
        

building_data = {'GIA' : 0.0, 'total_glazing_area_by_orientation': {
    'North': 0.0,
    'East': 0.0, 
    'South': 0.0, 
    'West': 0.0

       
}}




# 1) ROOMS 

rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()

room_data = {}

for room in rooms:

    # GET ROOM AREA

    number = room.Number
    area = DB.UnitUtils.ConvertFromInternalUnits(
        room.Area, 
        DB.UnitTypeId.SquareMeters
        )
    area = round(area, 2)
    name_parameter = room.GetParameter(DB.ParameterTypeId.RoomName)
    name = name_parameter.AsString()

    room_data[number] = {
        'room_name' : name,
        'room_area' : area,
        'glazing_area' : 0.0, 

        'glazing_by_orientation': {
            'North' : 0.0,
            'East' : 0.0,
            'South' : 0.0,
            'West' : 0.0
        }
        }




# 2) WINDOWS

windows = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()


for window in windows:

    # GET WINDOW AREA
  
    window_type = window.Symbol

    width_parameter = window_type.GetParameter(DB.ParameterTypeId.FamilyWidthParam)
    height_parameter = window_type.GetParameter(DB.ParameterTypeId.FamilyHeightParam)

    width = width_parameter.AsDouble()
    height = height_parameter.AsDouble()

    width_m = DB.UnitUtils.ConvertFromInternalUnits(
        width, 
        DB.UnitTypeId.Meters
        )
    
    height_m = DB.UnitUtils.ConvertFromInternalUnits(
        height, 
        DB.UnitTypeId.Meters
        )

    window_area = width_m * height_m


    # GET WINDOW LOCATION (ROOM) 

    to_room = window.ToRoom[phase]
    from_room = window.FromRoom[phase]

    if to_room is not None:
        room = to_room

    elif from_room is not None:
        room = from_room

    else:
        room = None

    if room is not None: 

        room_number = room.Number

        room_data[room_number]['glazing_area'] += window_area

        exterior_facing = get_exterior_facing(window, phase)

        if exterior_facing is not None:

            orientation = get_orientation(exterior_facing)

            room_data[room_number]['glazing_by_orientation'][orientation] += window_area

            building_data['total_glazing_area_by_orientation'][orientation] += window_area


        else:
            print(
                'Window | Room: {} | Orientation could not be determined'.format(
                    room_number
                )
            )

        #print("Room Name: {} | Window Area: {:.2f}sqm".format(room_name, window_area))

    else:
        print("NO ROOM | Window Area: {:.2f}sqm".format(window_area))



# 3) CURTAIN WALLING

curtain_panels = DB.FilteredElementCollector(doc) \
    .OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels) \
    .WhereElementIsNotElementType() \
    .ToElements()
   

#print('number_of_panels', len(curtain_panels))


for panel in curtain_panels:

    # GET PANEL AREA

    area_parameter = panel.GetParameter(
        DB.ParameterTypeId.HostAreaComputed
    )

    panel_area = area_parameter.AsDouble()

    panel_area_m2 = DB.UnitUtils.ConvertFromInternalUnits(
        panel_area, 
        DB.UnitTypeId.SquareMeters
    )


    # GET PANEL LOCATION (ROOM)

    # 1) Centre Of Panel

    bounding_box = panel.get_BoundingBox(None)

    centre = (bounding_box.Max + bounding_box.Min) * 0.5

    # 2) Perpendicular Vector

    direction = panel.FacingOrientation.Normalize()

    # 3) Offset Points

    offset = DB.UnitUtils.ConvertToInternalUnits(0.2, DB.UnitTypeId.Meters)

    point_1 = centre + direction * offset
    point_2 = centre - direction * offset

    # 4) Check Room For Each Point

    room_1 = doc.GetRoomAtPoint(point_1, phase)
    room_2 = doc.GetRoomAtPoint(point_2, phase)

    if room_1 is not None:
        room = room_1
    elif room_2 is not None:
        room = room_2

    else:
        room = None


    # ADD PANEL AREA TO ROOM DATA

    if room is not None:

        number = room.Number
        
        room_data[number]['glazing_area'] += panel_area_m2

        exterior_facing = get_exterior_facing(panel, phase)

        if exterior_facing is not None:
                
            orientation = get_orientation(exterior_facing)

            room_data[number]['glazing_by_orientation'][orientation] += panel_area_m2
            
            building_data['total_glazing_area_by_orientation'][orientation] += panel_area_m2

    else:

        print(
            "CURTAIN WALL PANEL HAS NO ROOM | Area: {:.2f}sqm".format(
                panel_area_m2
            )
        )



# 4) CALCULATE GLAZING RATIO PER ROOM = # (glazing area / room area) * 100 


for room_number in room_data:

    glazing_area = room_data[room_number]['glazing_area']
    room_area = room_data[room_number]['room_area']

    if room_area > 0:
        glazing_ratio = (glazing_area / room_area) * 100
    else:
        glazing_ratio = 0.0

    room_data[room_number]['glazing_ratio'] = glazing_ratio



# 5) MOST GLAZED ELEVATION

orientation_data = building_data['total_glazing_area_by_orientation']
most_glazed_elevation = max(orientation_data, key=orientation_data.get)
largest_glazed_area = orientation_data[most_glazed_elevation]

building_data['most_glazed_elevation'] = most_glazed_elevation
building_data['largest_glazed_area'] = largest_glazed_area



# 6) MOST GLAZED ROOM

most_glazed_room = None
most_glazed_room_number = None
glazing_area_most_glazed_room = 0.0

for room_number in room_data:
    room_name = room_data[room_number]['room_name']
    glazing_area = room_data[room_number]['glazing_area']
    
    if glazing_area > glazing_area_most_glazed_room:
        most_glazed_room = room_name
        most_glazed_room_number = room_number
        glazing_area_most_glazed_room = glazing_area

building_data['most_glazed_room_number'] = most_glazed_room_number
building_data['most_glazed_room'] = most_glazed_room
building_data['glazing_area_most_glazed_room'] = glazing_area_most_glazed_room
   

# 5) PRINT REPORT

for room_number in sorted(room_data):

    data = room_data[room_number]

    print(
        
        "{} - {} | Room Area: {:.2f}sqm | Glazing Area: {:.2f}sqm | Glazing Ratio: {:.2f}% | North:{:.2f}sqm East:{:.2f}sqm South:{:.2f}sqm West:{:.2f}sqm".format(
            room_number, 
            data['room_name'],
            data['room_area'],
            data['glazing_area'],
            data['glazing_ratio'],
            data['glazing_by_orientation']['North'],
            data['glazing_by_orientation']['East'],
            data['glazing_by_orientation']['South'],
            data['glazing_by_orientation']['West']
        )
    )

print()

print(
    
    "Total Glazing Area - North Elevation: {:.2f}sqm \n Total Glazing Area - East Elevation: {:.2f}sqm \n Total Glazing Area - South Elevation: {:.2f}sqm \n Total Glazing Area - West Elevation: {:.2f}sqm".format(
          building_data['total_glazing_area_by_orientation']['North'],
          building_data['total_glazing_area_by_orientation']['East'],
          building_data['total_glazing_area_by_orientation']['South'],
          building_data['total_glazing_area_by_orientation']['West']
      )    

)

print()

print(

    "Most Glazed Elevation - {}: {:.2f}sqm \n Most Glazed Room - {}. {}: {:.2f}sqm".format(
        building_data['most_glazed_elevation'], 
        building_data['largest_glazed_area'],
        building_data['most_glazed_room_number'],
        building_data['most_glazed_room'],
        building_data['glazing_area_most_glazed_room']

    )
)




# FIND DUPLICATED CURTAIN WALLS

# curtain_walls = []

# walls = DB.FilteredElementCollector(doc) \
#     .OfCategory(DB.BuiltInCategory.OST_Walls) \
#     .WhereElementIsNotElementType() \
#     .ToElements()

# for wall in walls:

#     wall_type = doc.GetElement(wall.GetTypeId())

#     if wall_type.Kind == DB.WallKind.Curtain:
#         curtain_walls.append(wall)


# for i in range(len(curtain_walls)):

#     wall_1 = curtain_walls[i]
#     curve_1 = wall_1.Location.Curve

#     p1 = curve_1.GetEndPoint(0)
#     p2 = curve_1.GetEndPoint(1)

#     for j in range(i + 1, len(curtain_walls)):

#         wall_2 = curtain_walls[j]
#         curve_2 = wall_2.Location.Curve

#         q1 = curve_2.GetEndPoint(0)
#         q2 = curve_2.GetEndPoint(1)

#         same_direction = (
#             p1.IsAlmostEqualTo(q1) and
#             p2.IsAlmostEqualTo(q2)
#         )

#         reverse_direction = (
#             p1.IsAlmostEqualTo(q2) and
#             p2.IsAlmostEqualTo(q1)
#         )

#         if same_direction or reverse_direction:

#             print(
#                 "POSSIBLE DUPLICATE CURTAIN WALLS: {} and {}".format(
#                     wall_1.Id,
#                     wall_2.Id
#                 )
#             )

     
        