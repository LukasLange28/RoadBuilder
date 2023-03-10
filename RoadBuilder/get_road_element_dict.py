import math

def get_line_dict(start, direction, length, factor):
    """
    Return dictionary for straight
    """
    dict = {}
    dict['name'] = 'line'
    dict['start'] = start
    dict['length'] = length 
    dict['direction'] = direction
    dict['endDirection'] = dict['direction']
    angle = math.radians(dict['direction'])
    dict['end'] = [get_int(dict['start'][0] + length * factor * math.cos(angle)), get_int(dict['start'][1] - length * factor * math.sin(angle))]
    return dict

def get_zebra_dict(start, direction, length, factor):
    """
    Return dictionary for straight with zebra
    """
    dict = {}
    dict['name'] = 'zebra'
    dict['start'] = start
    dict['length'] = length 
    dict['direction'] = direction
    dict['endDirection'] = dict['direction']
    angle = math.radians(dict['direction'])
    dict['end'] = [get_int(dict['start'][0] + length * factor * math.cos(angle)), get_int(dict['start'][1] - length * factor * math.sin(angle))]
    return dict

def get_blocked_area_dict(start, direction, length, factor):
    """
    Return dictionary for blocked area
    """
    dict = {}
    dict['name'] = 'blockedArea'
    dict['start'] = start
    dict['length'] = length 
    dict['direction'] = direction
    dict['endDirection'] = dict['direction']
    angle = math.radians(dict['direction'])
    dict['end'] = [get_int(dict['start'][0] + length * factor * math.cos(angle)), get_int(dict['start'][1] - length * factor * math.sin(angle))]
    return dict

def get_right_curve_dict(start, direction, radius, arcLength ,factor):
    """
    Return dictionary for right curve
    """
    dict = {}
    dict['name'] = 'circleRight'
    dict['radius'] = radius
    radius_pix = radius * factor
    dict['direction'] = direction
    direktion_angle = math.radians(dict['direction'])
    dict['start'] = [get_int(start[0] - radius_pix + radius_pix * math.sin(direktion_angle)), get_int(start[1] - radius_pix + radius_pix * math.cos(direktion_angle))]
    dict['arcLength'] = get_int(arcLength)
    dict['a'] = (90 + dict['direction'] - dict['arcLength'])*16
    angle = (90 + dict['direction'] - dict['arcLength'])/360*2*math.pi
    middle_point = [get_int(start[0] + radius_pix * math.sin(direktion_angle)), get_int(start[1] + radius_pix * math.cos(direktion_angle))]
    dict['end'] = [get_int(middle_point[0] + radius_pix * math.cos(angle)), get_int(middle_point[1] - radius_pix * math.sin(angle))]
    dict['endDirection'] = dict['direction']- dict['arcLength']
    return dict

def get_left_curve_dict(start, direction, radius, arcLength ,factor):
    """
    Return dictionary for left curve
    """
    dict = {}
    dict['name'] = 'circleLeft'
    dict['radius'] = radius
    radius_pix = radius * factor
    dict['direction'] = direction
    direktion_angle = math.radians(dict['direction'])
    dict['start'] = [get_int(start[0] - radius_pix - radius_pix * math.sin(direktion_angle)), get_int(start[1] - radius_pix - radius_pix * math.cos(direktion_angle))]
    dict['arcLength'] = get_int(arcLength)
    dict['a'] = (-90 + dict['direction'])*16
    angle = (-90 + dict['direction'] + dict['arcLength'])/360*2*math.pi
    middle_point = [get_int(start[0] - radius_pix * math.sin(direktion_angle)), get_int(start[1] - radius_pix * math.cos(direktion_angle))]
    dict['end'] = [get_int(middle_point[0] + radius_pix * math.cos(angle)), get_int(middle_point[1] - radius_pix * math.sin(angle))]
    dict['endDirection'] = dict['direction'] + dict['arcLength']
    return dict

def get_parking_area_dict(start, direction, length, right, left, factor):
    """
    Return dictionary for parking area
    """
    dict = {}
    dict['name'] = 'parkingArea'
    dict['start'] = start
    dict['direction'] = direction
    dict['endDirection'] = direction
    dict['length'] = length
    dict['right'] = right
    dict['left'] = left
    angle = math.radians(90 + direction)
    dict['end'] = [get_int(start[0] + length * factor * math.sin(angle)), get_int(start[1] + length * factor * math.cos(angle))]
    return dict

def get_intersection_dict(start, direction, text, length, open_intersections, factor):
    """
    Return dictionary for intersection
    """
    dict = {}
    arm_length = length/2*factor
    dict['name'] = 'intersection'
    dict['start'] = start
    dict['direction'] = direction
    dict['length'] = length
    angle = math.radians(dict['direction'])
    if text in ('Rechtskurve', 'RIGHT'):
        dict['text'] = 'RIGHT'
        dict['endDirection'] = direction - 90
        middle_point = [get_int(start[0] + arm_length * math.cos(angle)), get_int(start[1] - arm_length * math.sin(angle))]
        angle = math.radians(dict['endDirection'])
        dict['end'] = [get_int(middle_point[0] + arm_length * math.cos(angle)), get_int(middle_point[1] - arm_length * math.sin(angle))]
        # calculate the open ends of the intersetion
        open_direction_1 = dict['endDirection'] + 90
        angle = math.radians(open_direction_1)
        open_end1 = [get_int(middle_point[0] + arm_length * math.cos(angle)), get_int(middle_point[1] - arm_length * math.sin(angle))]
        open_direction_2 = open_direction_1 + 90
        angle = math.radians(open_direction_2)
        open_end_2 = [get_int(middle_point[0] + arm_length * math.cos(angle)), get_int(middle_point[1] - arm_length * math.sin(angle))]
        open_intersections.append({'openEnd': open_end1, 'openDirection': open_direction_1 + 180, 'newEnd': open_end_2, 'newDirection': open_direction_2, 'status': True, 'type': 'right','radius': length/2})
        open_intersections.append({ 'openEnd': open_end_2, 'openDirection': open_direction_2 + 180, 'newEnd': open_end1, 'newDirection': open_direction_1, 'status': True, 'type': 'left','radius': length/2})

    elif text in ('Linkskurve', 'LEFT'):
        dict['text'] = 'LEFT'
        dict['endDirection'] = direction + 90
        middle_point = [get_int(start[0] + arm_length * math.cos(angle)), get_int(start[1] - arm_length * math.sin(angle))]
        angle = math.radians(dict['endDirection'])
        dict['end'] = [get_int(middle_point[0] + arm_length * math.cos(angle)), get_int(middle_point[1] - arm_length * math.sin(angle))]
        # calculate the open ends of the intersetion
        open_direction_1 = dict['endDirection'] - 90
        angle = math.radians(open_direction_1)
        open_end1 = [get_int(middle_point[0] + arm_length * math.cos(angle)), get_int(middle_point[1] - arm_length * math.sin(angle))]
        open_direction_2 = open_direction_1 - 90
        angle = math.radians(open_direction_2)
        open_end_2 = [get_int(middle_point[0] + arm_length * math.cos(angle)), get_int(middle_point[1] - arm_length * math.sin(angle))]
        open_intersections.append({'openEnd': open_end1, 'openDirection': open_direction_1 + 180, 'newEnd': open_end_2, 'newDirection': open_direction_2, 'status': True, 'type': 'left','radius': length/2})
        open_intersections.append({ 'openEnd': open_end_2, 'openDirection': open_direction_2 + 180, 'newEnd': open_end1, 'newDirection': open_direction_1, 'status': True, 'type': 'right','radius': length/2})

    else:
        dict['text'] = 'STRAIGHT'
        dict['endDirection'] = direction
        angle = math.radians(dict['endDirection'])
        middle_point = [get_int(start[0] + arm_length * math.cos(angle)), get_int(start[1] - arm_length * math.sin(angle))]
        dict['end'] = [get_int(start[0] + 2 * arm_length * math.cos(angle)), get_int(start[1] - 2 * arm_length * math.sin(angle))]
        # calculate the open ends of the intersetion
        open_direction_1 = dict['endDirection'] - 90
        angle = math.radians(open_direction_1)
        open_end1 = [get_int(middle_point[0] + arm_length * math.cos(angle)), get_int(middle_point[1] - arm_length * math.sin(angle))]
        open_direction_2 = open_direction_1 - 180
        angle = math.radians(open_direction_2)
        open_end_2 = [get_int(middle_point[0] + arm_length * math.cos(angle)), get_int(middle_point[1] - arm_length * math.sin(angle))]
        open_intersections.append({'openEnd': open_end1, 'openDirection': open_direction_1 + 180, 'newEnd': open_end_2, 'newDirection': open_direction_2, 'status': True, 'type': 'straight','radius': length/2})
        open_intersections.append({ 'openEnd': open_end_2, 'openDirection': open_direction_2 + 180, 'newEnd': open_end1, 'newDirection': open_direction_1, 'status': True, 'type': 'straight','radius': length/2})
    # openIntersections.append({'openEnd': openEnd1, 'openDirection': openDirection1 + 180, 'newEnd': openEnd2, 'newDirection': openDirection2, 'status': True})
    # openIntersections.append({ 'openEnd': openEnd2, 'openDirection': openDirection2 + 180, 'newEnd': openEnd1, 'newDirection': openDirection1, 'status': True})
    return dict

def get_traffic_island_dict(start, direction, zebra_length, island_width, curve_area_length, curvature, factor):
    """
    Return dictionary for traffic island
    """
    dict = {}
    dict['name'] = 'trafficIsland'
    dict['start'] = start
    dict['direction'] = direction
    dict['endDirection'] = direction
    dict['zebraLength'] = zebra_length
    dict['islandWidth'] =island_width
    dict['curveAreaLength'] = curve_area_length
    dict['curvature'] = curvature
    length = (zebra_length + 2 * curve_area_length)*factor
    angle = math.radians(direction)
    dict['end'] = [get_int(start[0] + length * math.cos(angle)), get_int(start[1] - length * math.sin(angle))]
    return dict

def get_clothoid_dict(start, direction, a, angle, angle_offset, type, end, localDirection):
    dict = {}
    dict['name'] = 'clothoid'
    dict['start'] = start
    dict['direction'] = direction
    dict['a'] = a
    dict['angle'] = angle
    dict['angleOffset'] = angle_offset
    dict['type'] = type
    dict['localEnd'] = end
    dict['localDirection'] = localDirection
    radian = math.radians(direction)
    dict['end'] = [get_int(end[0]*math.cos(radian) + end[1]*math.sin(radian))+start[0], get_int(-end[0]*math.sin(radian) + end[1]*math.cos(radian))+start[1]]
    dict['endDirection'] = direction + angle
    return dict

def check_for_intersection_connection(end, direction, open_intersections):
    '''
    Checks if the last roadsection is connected to a open intersection.
    If true the open intersection will be integrated.
    '''
    for idx, open_road in enumerate(open_intersections):
        if end == open_road['openEnd'] and direction % 360 == open_road['openDirection'] % 360 and open_road['status']:
            new_end = open_road['newEnd']
            new_direction = open_road['newDirection']
            open_intersections[idx]['status'] = False
            if open_intersections[idx-1]['openEnd'] == open_road['newEnd']:
                open_intersections[idx-1]['status'] = False
            else:
                open_intersections[idx+1]['status'] = False
            return new_end, new_direction, open_intersections[idx]['type'], open_intersections[idx]['radius']
    return end, direction, None, None

def get_int(number):
    """
    Return the rounded number
    """
    return int(number + 0.5 if number >= 0 else number -0.5)

def get_faculty(number):
    """
    Return the faculty of number
    """
    faculty = 1
    for i in range(1,number):
        faculty *= i
    return faculty

def move_point(point, postponmet):
    return [point[0] + postponmet[0], point[1] + postponmet[1]]

def rotate_point(point, radian):
    return [get_int(point[0]*math.cos(radian)+point[1]*math.sin(radian)), get_int(-point[0]*math.sin(radian)+point[1]*math.cos(radian))]