import sys
import os
import shutil
import math
import importlib

from RoadBuilder.get_road_element_dict import *

def python_writer(road, file_name, close_loop):
    """
    Create the python-script for the given raod.
    closeLoop is a bool value. 
    close = True -> inserts close_loop() function
    """
    def get_line_style_text(element):
        """
        Return the string for the lines
        """
        return f'\t\tleft_line_marking=\'{element["leftLine"]}\',\n '\
            f'\t\tmiddle_line_marking=\'{element["middleLine"]}\',\n'\
            f'\t\tright_line_marking=\'{element["rightLine"]}\',\n'
    # Sizes of the two parkiong spot typs
    parking_spot_size = [[0.7, 0.3], [0.3, 0.5]]

    # Open the file/ The file will be created if not exist
    with open(file_name, 'w+') as file:
        file.write('import math\n')
        file.write('from simulation.utils.road.road import Road  # Definition of the road class\n')
        file.write('from simulation.utils.road.sections import (\n'
        '\tIntersection,\n'
        '\tLeftCircularArc,\n'
        '\tRightCircularArc,\n'
        '\tParkingArea,\n'
        '\tParkingLot,\n'
        '\tParkingObstacle,\n'
        '\tParkingSpot,\n'
        '\tStraightRoad,\n'
        '\tZebraCrossing,\n'
        '\tBlockedArea,\n'
        '\tTrafficIsland,\n'
        ')\n')
        file.write('from simulation.utils.road.sections.road_section import RoadSection\n')
        file.write('road = Road()\n')
        # for-loop iterates through the road
        for element in road:
            if element['name'] == 'line':
                length = element['length']
                file.write(f'road.append(\n')
                file.write(f'\tStraightRoad(\n')
                file.write(f'\t\tlength={length},\n')
                file.write(get_line_style_text(element))
                file.write(f'\t)\n')
                file.write(f')\n')
            elif element['name'] == 'circleRight':
                file.write('road.append(\n')
                file.write('\tRightCircularArc(\n')
                radius=element['radius']
                file.write(f'\t\tradius={radius},\n')
                angle=element['arcLength']
                file.write(f'\t\tangle=math.radians({angle}),\n')
                file.write(get_line_style_text(element))
                file.write('\t)\n')
                file.write(')\n')
            elif element['name'] == 'circleLeft':
                file.write('road.append(\n')
                file.write('\tLeftCircularArc(\n')
                radius=element['radius']
                file.write(f'\t\tradius={radius},\n')
                angle=element['arcLength']
                file.write(f'\t\tangle=math.radians({angle}),\n')
                file.write(get_line_style_text(element))
                file.write('\t)\n')
                file.write(')\n')
            elif element['name'] == 'zebra':
                length = element['length']
                file.write(f'road.append(\n')
                file.write(f'\tZebraCrossing(\n')
                file.write(f'\t\tlength={length},\n')
                file.write(get_line_style_text(element))
                file.write(f'\t)\n')
                file.write(f')\n')
            elif element['name'] == 'blockedArea':
                length = element['length']
                file.write(f'road.append(\n')
                file.write(f'\tBlockedArea(\n')
                file.write(f'\t\tlength={length},\n')
                file.write(f'\t\twidth=0.2,\n')
                file.write(get_line_style_text(element))
                file.write(f'\t)\n')
                file.write(f')\n')
            elif element['name'] == 'trafficIsland':
                file.write('road.append(\n')
                file.write('\tTrafficIsland(\n')
                file.write(f'\t\tisland_width={element["islandWidth"]},\n')
                file.write(f'\t\tzebra_length={element["zebraLength"]},\n')
                file.write(f'\t\tcurve_area_length={element["curveAreaLength"]},\n')
                file.write(f'\t\tcurvature={element["curvature"]},\n')
                file.write('\t\tzebra_marking_type=TrafficIsland.ZEBRA,\n')
                file.write(get_line_style_text(element))
                file.write('))\n')
            elif element['name'] == 'intersection':
                file.write(f'road.append(\n')
                file.write(f'\tIntersection(\n')
                file.write(f'\t\tsize={element["length"]},\n')
                file.write(f'\t\tturn=Intersection.{element["text"]},\n')
                file.write(f'\t\tangle=math.radians(90),\n')
                file.write(get_line_style_text(element))
                file.write(f'\t)\n')
                file.write(f')\n')
            elif element['name'] == 'parkingArea':
                file.write('road.append(\n')
                file.write('\tParkingArea(\n')
                file.write(f'\t\tlength={element["length"]},\n')
                file.write(f'\t\tstart_line=False,\n')
                file.write(get_line_style_text(element))
                file.write(f'\t\tleft_lots=[\n')
                for lot in element['left']:
                    file.write(f'\t\t\tParkingLot(\n')
                    file.write(f'\t\t\t\tstart={lot["start"]},\n')
                    file.write(f'\t\t\t\topening_angle=math.radians(40),\n')
                    file.write(f'\t\t\t\tdepth={parking_spot_size[lot["type"]][1]},\n')
                    file.write(f'\t\t\t\tspots=[\n')
                    for spot in lot['spots']:
                        obstacle = ', obstacle=ParkingObstacle()' if spot == 'OCCUPIED' else ''
                        file.write(f'\t\t\t\tParkingSpot(kind=ParkingSpot.{spot}, width={parking_spot_size[lot["type"]][0]}{obstacle}),\n')
                    file.write(f'\t\t\t\t]\n')
                    file.write(f'\t\t\t),\n')
                file.write(f'\t\t],\n')
                file.write(f'\t\tright_lots=[\n')
                for lot in element['right']:
                    file.write(f'\t\t\tParkingLot(\n')
                    file.write(f'\t\t\t\tstart={lot["start"]},\n')
                    file.write(f'\t\t\t\topening_angle=math.radians(40),\n')
                    file.write(f'\t\t\t\tdepth={parking_spot_size[lot["type"]][1]},\n')
                    file.write(f'\t\t\t\tspots=[\n')
                    for spot in lot['spots']:
                        obstacle = ', obstacle=ParkingObstacle()' if spot == 'OCCUPIED' else ''
                        file.write(f'\t\t\t\tParkingSpot(kind=ParkingSpot.{spot}, width={parking_spot_size[lot["type"]][0]}{obstacle}),\n')
                    file.write(f'\t\t\t\t]\n')
                    file.write(f'\t\t\t),\n')
                file.write(f'\t\t],\n')
                file.write('\t)\n')
                file.write(')\n')
            elif element['name'] == 'clothoid':
                raise Exception('Es können keine Klothoiden im Python Format gespeichert werden')
            if element.get('skip_intersection'):
                if element['skip_intersection'] == 'right':
                    file.write('road.append(\n')
                    file.write('\tRightCircularArc(\n')
                    radius=element['intersection_radius']
                    file.write(f'\t\tradius={radius},\n')
                    file.write(f'\t\tangle=math.radians(90),\n')
                    file.write("\t\tleft_line_marking='missing',\n ")
                    file.write("\t\tmiddle_line_marking='missing',\n ")
                    file.write("\t\tright_line_marking='missing',\n ")
                    file.write('\t)\n')
                    file.write(')\n')
                elif element['skip_intersection'] == 'left':
                    file.write('road.append(\n')
                    file.write('\tLeftCircularArc(\n')
                    radius=element['intersection_radius']
                    file.write(f'\t\tradius={radius},\n')
                    file.write(f'\t\tangle=math.radians(90),\n')
                    file.write("\t\tleft_line_marking='missing',\n ")
                    file.write("\t\tmiddle_line_marking='missing',\n ")
                    file.write("\t\tright_line_marking='missing',\n ")
                    file.write('\t)\n')
                    file.write(')\n')
                elif element['skip_intersection'] == 'straight':
                    length = element['intersection_radius']*2
                    file.write(f'road.append(\n')
                    file.write(f'\tStraightRoad(\n')
                    file.write(f'\t\tlength={length},\n')
                    file.write("\t\tleft_line_marking='missing',\n ")
                    file.write("\t\tmiddle_line_marking='missing',\n ")
                    file.write("\t\tright_line_marking='missing',\n ")
                    file.write(f'\t)\n')
                    file.write(f')\n')
                
        if close_loop: file.write('road.close_loop()')

def python_reader(file_name, parent_window):
    """
    Generates a new file with the code from the given python script
    Runs the new file and gets the road as a return value
    Create parentWindow.road with the returned road
    """
    # newCode is a string of code for the new file
    new_code = []
    # the code from the  new file will be a function with a return value
    new_code.append('def roadFunc():\n')
    with open(file_name, 'r') as file:
        data = file.readlines()
        for line in data:
            # StaticObstacle will be replaced because the StaticObstacle class is not existing
            new_code.append(f'\t{line.replace("StaticObstacle", "Obstacle")}')
    new_code.append('\n\treturn road.sections')
    delete_temp = False
    # Create the directory temp if not exist
    if not os.path.exists(os.path.join(os.path.dirname(file_name), 'temp')):
        os.makedirs(os.path.join(os.path.dirname(file_name), 'temp'))
        delete_temp = True
    with open(f'{os.path.dirname(file_name)}/temp/newFile.py','w+') as file:
        for line in new_code:
            file.write(line)
    # if the path of the given file is not in the sys.path it will be appended
    delete_sys_path = False
    if not os.path.dirname(file_name) in sys.path:
        delete_sys_path = True
        # Insert new searchpath for imports
        sys.path.append(os.path.dirname(file_name))
    # Import the new file
    from temp import newFile
    # Reload the import for the case that the pythonReader is used more than one time in a row
    importlib.reload(newFile)
    # Imports the road elements
    from simulation.utils.road.road import Road
    from simulation.utils.road.sections import (
        Intersection,
        LeftCircularArc,
        RightCircularArc,
        ParkingArea,
        ParkingLot,
        ParkingObstacle,
        ParkingSpot,
        StraightRoad,
        ZebraCrossing,
        BlockedArea,
        TrafficIsland,
    )
    from simulation.utils.road.sections.road_section import RoadSection
    
    # Run the new file
    py_road = newFile.roadFunc()

    # Delete the old road
    parent_window.road.clear()
    parent_window.list_widget.clear()
    # Create the new road
    parent_window.road.append({'name': 'firstElement', 'start': parent_window.start, 'end': parent_window.start, 'direction': parent_window.direction, 'endDirection': parent_window.direction})
    for element in py_road:
        if parent_window.road[-1]['end'] != check_for_intersection_connection(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], parent_window.open_intersections)[0]:
            #road_element['end'], road_element['endDirection'], road_element['skip_intersection'], road_element['intersection_radius'] = check_for_intersection_connection(road_element['end'], road_element['endDirection'], self.open_intersections)
            continue
        elif type(element) == StraightRoad:
            dict = get_line_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], element.length, parent_window.factor)
        elif type(element) == RightCircularArc:
            dict = get_right_curve_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], element.radius, math.degrees(element.angle), parent_window.factor)
        elif type(element) == LeftCircularArc:
            dict = get_left_curve_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], element.radius, math.degrees(element.angle), parent_window.factor)
        elif type(element) == ZebraCrossing:
            dict = get_zebra_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], element.length, parent_window.factor)
        elif type(element) == BlockedArea:
            dict = get_blocked_area_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], element.length, parent_window.factor)
        elif type(element) == TrafficIsland:
            dict = get_traffic_island_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'],element.zebra_length, element.island_width, element.curve_area_length, element.curvature, parent_window.factor)
        elif type(element) == Intersection:
            turn = ['STRAIGHT', 'LEFT', 'RIGHT']
            dict = get_intersection_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], turn[element.turn], element.size, parent_window.open_intersections, parent_window.factor)
        elif type(element) == ParkingArea:
            kind = ['FREE', 'OCCUPIED', 'BLOCKED']
            left = [{'start': parkSpot.start, 'number': len(parkSpot.spots), 'spots': [kind[spot.kind] for spot in parkSpot.spots], 'type': 1 if parkSpot.depth >= 0.5 else 0} for parkSpot in element.left_lots]
            right = [{'start': parkSpot.start, 'number': len(parkSpot.spots), 'spots': [kind[spot.kind] for spot in parkSpot.spots], 'type': 1 if parkSpot.depth >= 0.5 else 0} for parkSpot in element.right_lots]
            dict = get_parking_area_dict(parent_window.road[-1]['end'], parent_window.road[-1]['endDirection'], element.length, right, left, parent_window.factor)
        else:
            continue

        dict['leftLine'] = element.left_line_marking
        dict['middleLine'] = element.middle_line_marking
        dict['rightLine'] = element.right_line_marking

        parent_window.append_road_element(dict, True)

    # remove syspath if appended
    if delete_sys_path:
        sys.path.remove(os.path.dirname(file_name))
    if delete_temp:
        shutil.rmtree(os.path.join(os.path.dirname(file_name), 'temp'))

    