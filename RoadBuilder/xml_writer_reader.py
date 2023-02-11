from xml.etree import cElementTree as ET, ElementTree
from xml.etree import ElementTree
from xml.dom import minidom

from get_road_element_dict import *

def xml_writer(road, file_name, factor):
    """
    Generate xml file for given road.
    """
    parking_spot_size = [[0.7, 0.3], [0.3, 0.5]]
    size, start = get_xml_size(road, factor)
    # Top node
    root = ET.Element('TrackDefinition', {'version': '0.0.1'})
    ET.SubElement(root, 'Size', {'width': str(size[0]), 'height': str(size[1])})
    ET.SubElement(root, 'Origin', {'x': '0', 'y': '0'})
    ET.SubElement(root, 'Background', {'color': '#545454', 'opacity': '1.0'})
    
    segments = ET.SubElement(root, 'Segments')
    ET.SubElement(segments, 'Start', {'x': str(start[0]), 'y': str(start[1]), 'direction_angle': '0'})
    
    for element in road:
        if element['name'] == 'line':
            ET.SubElement(segments, 'Straight', {'length': str(element['length'])})
        elif element['name'] == 'circleRight':
            ET.SubElement(segments, 'Turn', {'direction': 'right', 'radius': str(element['radius']), 'radian': str(element['arcLength'])})
        elif element['name'] == 'circleLeft':
            ET.SubElement(segments, 'Turn', {'direction': 'left', 'radius': str(element['radius']), 'radian': str(element['arcLength'])})
        elif element['name'] == 'zebra':
            ET.SubElement(segments, 'Crosswalk', {'length': str(element['length'])})
        elif element['name'] == 'blockedArea':
            ET.SubElement(segments, 'BlockedArea', {'length': str(element['length'])})
        elif element['name'] == 'trafficIsland':
            ET.SubElement(segments, 'TrafficIsland', {'island_width': str(element['islandWidth']), 'crosswalk_length': str(element['zebraLength']), 'curve_segment_length': str(element['curveAreaLength']), 'curvature': str(element['curvature'])})
        elif element['name'] == 'intersection':
            ET.SubElement(segments, 'Intersection', {'length': str(element['length']), 'direction': element['text'].lower()})
        elif element['name'] == 'parkingArea':
            parking_area = ET.SubElement(segments, 'ParkingArea', {'length': str(element['length'])})
            right_lots = ET.SubElement(parking_area, 'RightLots')
            for lot in element['right']:
                parking_lot = ET.SubElement(right_lots, 'ParkingLot', {'start': str(lot['start']), 'depth': str(parking_spot_size[lot['type']][1]), 'opening_ending_angle': '45'})#, 'lot_length': str(parkingSpotSize[lot['type']][0])})
                for spot in lot['spots']:
                    ET.SubElement(parking_lot, 'Spot', {'type': spot.lower(), 'length': str(parking_spot_size[lot['type']][0])})
            left_lots = ET.SubElement(parking_area, 'LeftLots')
            for lot in element['left']:
                parking_lot = ET.SubElement(left_lots, 'ParkingLot', {'start': str(lot['start']), 'depth': str(parking_spot_size[lot['type']][1]), 'opening_ending_angle': '45'})#, 'lot_length': str(parkingSpotSize[lot['type']][0])})
                for spot in lot['spots']:
                    ET.SubElement(parking_lot, 'Spot', {'type': spot.lower(), 'length': str(parking_spot_size[lot['type']][0])})
        elif element['name'] == 'clothoid':
            direction = 'right' if element['angle'] < 0 else 'left'
            ET.SubElement(segments, 'Clothoid', {'a': str(element['a']), 'angle': str(abs(element['angle'])), 'angle_offset': str(element['angleOffset']), 'direction': direction, 'type': str(element['type'])})
        if element.get('skip_intersection'):
            ET.SubElement(segments, 'Gap', {'direction': element['skip_intersection'], 'length': str(element['intersection_radius']*2)})
    
    with open(file_name, 'w') as f:
        f.write(minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(indent='\t'))
    

def get_xml_size(road, factor):
    """
    Return the dimensions of the road and the start point in these dimensions
    """
    coordinates = {'x':0, 'y':0, '-x':0, '-y':0}
    for element in road:

        # points is a list of points that could stick out of the dimensions
        points =[]
        if element['name'] == 'line' or element['name'] == 'zebra' or element['name'] == 'blockedArea':
            points.append(element['end'])
        elif element['name'] == 'circleRight' or element['name'] == 'circleLeft':
            points.append(element['start'])
            points.append([element['start'][0]+element['radius']*2*factor, element['start'][1]+element['radius']*2*factor])
        elif element['name'] == 'trafficIsland':
            points.append([get_int(element['start'][0] + element['islandWidth'] * math.cos(math.radians(element['direction']))), get_int(element['start'][1] - element['islandWidth'] * math.sin(math.radians(element['direction'])))])
            points.append([get_int(element['end'][0] - element['islandWidth'] * math.cos(math.radians(element['direction']))), get_int(element['end'][1] + element['islandWidth'] * math.sin(math.radians(element['direction'])))])
        elif element['name'] == 'intersection':
            points.append([get_int(element['start'][0] + element['length'] * math.cos(math.radians(element['direction']))), get_int(element['start'][1] - element['length'] * math.sin(math.radians(element['direction'])))])
            points.append([get_int(element['end'][0] - element['length'] * math.cos(math.radians(element['direction']))), get_int(element['end'][1] + element['length'] * math.sin(math.radians(element['direction'])))])
        elif element['name'] == 'parkingArea':
            points.append([get_int(element['start'][0] + 1/factor * math.cos(math.radians(element['direction']))), get_int(element['start'][1] - 1/factor * math.sin(math.radians(element['direction'])))])
            points.append([get_int(element['end'][0] - 1/factor * math.cos(math.radians(element['direction']))), get_int(element['end'][1] + 1/factor * math.sin(math.radians(element['direction'])))])
        elif element['name'] == 'clothoid':
            points.append(element['start'])
            invert = 1 if element['angle'] < 0 else -1
            new_point = rotate_point([element['a']*3, element['a']*3*invert], math.radians(element['direction']))
            points.append([element['start'][0] + new_point[0], element['start'][1] + new_point[1]])

        for point in points:
            # -10000 to get meter
            if (point[0]-10000)/factor > coordinates['x']:
                coordinates['x'] = (point[0]-10000)/factor
            elif (point[0]-10000)/factor < coordinates['-x']:
                coordinates['-x'] = (point[0]-10000)/factor
            if (point[1]-10000)/factor > coordinates['y']:
                coordinates['y'] = (point[1]-10000)/factor
            elif (point[1]-10000)/factor < coordinates['-y']:
                coordinates['-y'] = (point[1]-10000)/factor
        
    size = [-coordinates['-x']+coordinates['x']+2, -coordinates['-y']+coordinates['y']+2]
    start = [-coordinates['-x']+1, coordinates['y']+1]
    return size, start

def xml_reader(file_name, parent_window):
    """
    Get the road from the given xml file
    """
    tree = ElementTree.parse(file_name)
    root = tree.getroot()
    segments = root.find('Segments')
    # Delete the old road
    parent_window.road.clear()
    parent_window.list_widget.clear()
    parent_window.road.append({'name': 'firstElement', 'start': parent_window.start, 'end': parent_window.start, 'direction': parent_window.direction, 'endDirection': parent_window.direction})
    for element in segments:
        if element.tag == 'Start' or element.tag == 'Gap':
            continue
        elif element.tag == 'Straight':
            length = float(element.get('length')) if element.get('length') else 1
            dict = get_line_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], length, parent_window.factor)
        elif element.tag == 'Turn':
            radius = float(element.get('radius')) if element.get('radius') else 1
            radian = float(element.get('radian')) if element.get('radian') else 90
            if element.get('direction') == 'right':
                dict = get_right_curve_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], radius, radian, parent_window.factor)
            elif element.get('direction') == 'left':
                dict = get_left_curve_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], radius, radian, parent_window.factor)
        elif element.tag == 'Crosswalk':
            length = float(element.get('length')) if element.get('length') else 1
            dict = get_zebra_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], length, parent_window.factor)
        elif element.tag == 'BlockedArea':
            length = float(element.get('length')) if element.get('length') else 1
            dict = get_blocked_area_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], length, parent_window.factor)
        elif element.tag == 'TrafficIsland':
            zebra_length = float(element.get('zebra_length')) if element.get('zebra_length') else 1
            island_width = float(element.get('island_width')) if element.get('island_width') else 1
            curve_area_length = float(element.get('curve_area_length')) if element.get('curve_area_length') else 1
            curvature = float(element.get('curvature')) if element.get('curvature') else 0.5
            dict = get_traffic_island_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], zebra_length, island_width, curve_area_length, curvature, parent_window.factor)
        elif element.tag == 'Intersection':
            direction = element.get('direction').upper() if element.get('direction') else 'STRAIGHT'
            size = float(element.get('length')) if element.get('length') else 2
            dict = get_intersection_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], direction, size, parent_window.open_intersections, parent_window.factor)
        elif element.tag == 'ParkingArea':  
            left = [{'start': float(parkSpot.get('start')), 'number': len(parkSpot.findall('Spot')), 'spots': [spot.get('type').upper() for spot in parkSpot.findall('Spot')], 'type': 1 if float(parkSpot.get('depth')) >= 0.5 else 0} for parkSpot in element.find('LeftLots').findall('ParkingLot')]
            right = [{'start': float(parkSpot.get('start')), 'number': len(parkSpot.findall('Spot')), 'spots': [spot.get('type').upper() for spot in parkSpot.findall('Spot')], 'type': 1 if float(parkSpot.get('depth')) >= 0.5 else 0} for parkSpot in element.find('RightLots').findall('ParkingLot')]
            length = float(element.get('length')) if element.get('length') else 5
            dict = get_parking_area_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], length, right, left, parent_window.factor)
        
        # Road line are not given in the xml file
        dict['leftLine'] = 'solid'
        dict['middleLine'] = 'dashed'
        dict['rightLine'] = 'solid'

        parent_window.append_road_element(dict)
    parent_window.reconnect_road(0)
    