import sys, os
import math
import shutil

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QMessageBox, QFileDialog, QFormLayout, QGroupBox, QShortcut, QWidget
from PyQt5.QtGui import QPainter, QPen, QFont, QPainterPath, QPolygonF, QTransform, QKeySequence
from PyQt5.QtCore import Qt, QPoint, QLineF
from PyQt5.QtSvg import QSvgWidget

# Development: insert python search path to use your own track_generator version
#if  not '/home/id305564/Schreibtisch/U/track_generator' in sys.path:
#    sys.path.append('/home/id305564/Schreibtisch/U/track_generator')

import clothoids_window, parking_area, traffic_island, intersection, select_line_style
from RoadBuilder.get_road_element_dict import *
from RoadBuilder.python_writer_reader import python_reader, python_writer
from RoadBuilder.xml_writer_reader import xml_writer, xml_reader
from RoadBuilder.preview_window import SvgWidget
from track_generator.generator import generate_track

class MainWindow(QMainWindow):
    
    def __init__(self):
        
        super().__init__()       
        self.move_window = QPoint(0,0)
        
        # Road position
        self.start = [0, 0]
        self.direction = 0

        # One meter = 100 pixel
        self.factor = 100
        # Different parking spot sizes
        self.parking_spot_size = [[0.7, 0.3], [0.3, 0.5]]
        
        # road list
        self.road = []
        self.road.append({'name': 'firstElement', 'start': self.start, 'end': self.start, 'direction': self.direction, 'endDirection': self.direction})
        
        # list for open intersection ends
        self.open_intersections = []
        
        # creates widget for road presentation
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.svg_widget = SvgWidget(self)
        self.scene.addWidget(self.svg_widget)
        self.setCentralWidget(self.view)

        # creates shortcuts
        QShortcut(QKeySequence(QtCore.Qt.Key_Minus), self.view, context=QtCore.Qt.WidgetShortcut, activated=self.zoom_out)
        QShortcut(QKeySequence(QtCore.Qt.Key_Plus), self.view, context=QtCore.Qt.WidgetShortcut, activated=self.zoom_in)

        self.setWindowTitle('RoadBuilder')
        font = QFont('Roboto', 10)
        self.setFont(font)

        screen_width = QtWidgets.QDesktopWidget().screenGeometry(-1).width()
        button_width = 180
        self.button_width = button_width
        
        # graphic elements
        self.end_label = QLabel(f'x: {self.road[-1]["end"][0]/self.factor}, y: {self.road[-1]["end"][1]/self.factor}')
        self.direction_label = QLabel(f'{self.road[-1]["endDirection"]%360}°')

        form = QFormLayout()
        form.setVerticalSpacing(0)
        form.addRow(QLabel('Start:'), QLabel(f'x: {self.start[0]/self.factor}, y: {self.start[1]/self.factor}'))
        form.addRow(QLabel('Ende:'), self.end_label)
        form.addRow(QLabel('Richtung:'), self.direction_label)

        form_group_box = QGroupBox(self)
        form_group_box.setLayout(form)
        form_group_box.setMinimumSize(200,100)
        form_group_box.move(200, 0)

        self.list_widget= QtWidgets.QListWidget(self)
        self.list_widget.resize(200, 300)
        self.list_widget.setWindowTitle('Strecke')
        self.list_widget.setToolTip('Hier erscheinen die Streckenabschnitte')
        self.list_widget.move(0, 20)
        
        delete_button = QPushButton('Streckenelement löschen', self)
        delete_button.setToolTip('Das ausgewählte Element wird gelöscht')
        delete_button.move(0, 320)
        delete_button.clicked.connect(self.delete_list_element)
        delete_button.setFixedWidth(200)
        
        save_python_button = QPushButton('Speichern', self)
        save_python_button.setToolTip('Die Strecke wird als Python Datei gespeichert')
        save_python_button.move(screen_width-button_width-20, 10)
        save_python_button.clicked.connect(self.save_python_button_clicked)
        save_python_button.setFixedWidth(75)
        
        load_python_button = QPushButton('Laden', self)
        load_python_button.setToolTip('Die Strecke wird aus einer Python Datei geladen')
        load_python_button.move(screen_width-button_width-20, 40)
        load_python_button.clicked.connect(self.load_python_button_clicked)
        load_python_button.setFixedWidth(75)
        
        kitcar_form = QFormLayout()
        kitcar_form.setVerticalSpacing(0)
        kitcar_form.addRow(QLabel('KITcar:'))
        kitcar_form.addRow(save_python_button, load_python_button)

        self.kitcar_form_group_box = QGroupBox(self)
        self.kitcar_form_group_box.setLayout(kitcar_form)
        self.kitcar_form_group_box.setMinimumSize(180, 80)
        self.kitcar_form_group_box.move(screen_width-button_width-20, 10)
        
        save_xml_button = QPushButton('Speichern', self)
        save_xml_button.setToolTip('Die Strecke wird als XML Datei gespeichert')
        save_xml_button.move(screen_width-button_width-20, 10)
        save_xml_button.clicked.connect(self.save_xml_button_clicked)
        save_xml_button.setFixedWidth(75)
        
        load_xml_button = QPushButton('Laden', self)
        load_xml_button.setToolTip('Die Strecke wird aus einer XML Datei geladen')
        load_xml_button.move(screen_width-button_width-20, 40)
        load_xml_button.clicked.connect(self.load_xml_button_clicked)
        load_xml_button.setFixedWidth(75)
        
        track_generator_form = QFormLayout()
        track_generator_form.setVerticalSpacing(0)
        track_generator_form.addRow(QLabel('Track Generator:'))
        track_generator_form.addRow(save_xml_button, load_xml_button)

        self.track_generator_form_group_box = QGroupBox(self)
        self.track_generator_form_group_box.setLayout(track_generator_form)
        self.track_generator_form_group_box.setMinimumSize(180, 80)
        self.track_generator_form_group_box.move(screen_width-button_width-20, 100)
        
        self.line_length = QLineEdit(self)
        self.line_length.move(screen_width-button_width-20, 230)
        self.line_length.setToolTip('Länge des Abschnitts')
        self.line_length.setPlaceholderText('Länge')
        self.line_length.setFixedWidth(button_width)
        self.line_length.setValidator(QtGui.QDoubleValidator())
        
        self.line_button = QPushButton('Gerade einfügen', self)
        self.line_button.setToolTip('Es wird eine Gerade eingefügt')
        self.line_button.move(screen_width-button_width-20, 260)
        self.line_button.clicked.connect(self.line_button_clicked)
        self.line_button.setFixedWidth(button_width)
        
        self.zebra_button = QPushButton('Zebrasteifen einfügen', self)
        self.zebra_button.setToolTip('Es wird eine Gerade mit Zebrastreifen eingefügt')
        self.zebra_button.move(screen_width-button_width-20, 290)
        self.zebra_button.clicked.connect(self.zebra_button_clicked)
        self.zebra_button.setFixedWidth(button_width)
        
        self.blocked_area_button = QPushButton('Hindernis einfügen', self)
        self.blocked_area_button.setToolTip('Es wird eine Gerade mit Hindernis eingefügt')
        self.blocked_area_button.move(screen_width-button_width-20, 320)
        self.blocked_area_button.clicked.connect(self.blocked_area_button_clicked)
        self.blocked_area_button.setFixedWidth(button_width)
        
        self.radius = QLineEdit(self)
        self.radius.setToolTip('Radius der Kurve')
        self.radius.setPlaceholderText('Radius')
        self.radius.move(screen_width-button_width-20, 380)
        self.radius.setFixedWidth(button_width)
        self.radius.setValidator(QtGui.QDoubleValidator())
        
        self.arc_length = QLineEdit(self)
        self.arc_length.setToolTip('Winkel der Kurve')
        self.arc_length.setPlaceholderText('Winkel')
        self.arc_length.move(screen_width-button_width-20, 410)
        self.arc_length.setFixedWidth(button_width)
        self.arc_length.setValidator(QtGui.QIntValidator())
        
        self.right_curve_button = QPushButton('Rechts Kurve einfügen', self)
        self.right_curve_button.setToolTip('Es wird eine Rechtskurve eingefügt')
        self.right_curve_button.move(screen_width-button_width-20, 440)
        self.right_curve_button.clicked.connect(self.right_curve_button_clicked)
        self.right_curve_button.setFixedWidth(button_width)
        
        self.left_curve_button = QPushButton('Links Kurve einfügen', self)
        self.left_curve_button.setToolTip('Es wird eine Linkskurve eingefügt')
        self.left_curve_button.move(screen_width-button_width-20, 470)
        self.left_curve_button.clicked.connect(self.left_curve_button_clicked)
        self.left_curve_button.setFixedWidth(button_width)
        
        self.clothoid_button = QPushButton('Klothoide einfügen', self)
        self.clothoid_button.setToolTip('Es wird ein Klothoid eingefügt')
        self.clothoid_button.move(screen_width-button_width-20, 500)
        self.clothoid_button.clicked.connect(self.clothoid_button_clicked)
        self.clothoid_button.setFixedWidth(button_width)

        self.parking_area_button = QPushButton('Parkbereich einfügen', self)
        self.parking_area_button.setToolTip('Es wird ein Parkbereich eingefügt')
        self.parking_area_button.move(screen_width-button_width-20, 560)
        self.parking_area_button.clicked.connect(self.parking_area_button_clicked)
        self.parking_area_button.setFixedWidth(button_width)
        
        self.traffic_island_button = QPushButton('Fußgängerinsel einfügen', self)
        self.traffic_island_button.setToolTip('Es wird eine Fußgängerinsel eingefügt')
        self.traffic_island_button.move(screen_width-button_width-20, 590)
        self.traffic_island_button.clicked.connect(self.traffic_island_button_clicked)
        self.traffic_island_button.setFixedWidth(button_width)
        
        self.intersection_button = QPushButton('Kreuzung einfügen', self)
        self.intersection_button.setToolTip('Es wird eine Kreuzung eingefügt')
        self.intersection_button.move(screen_width-button_width-20, 620)
        self.intersection_button.clicked.connect(self.intersection_button_clicked)
        self.intersection_button.setFixedWidth(button_width)
        
        self.update_svg()
        self.showMaximized()
        
    def resizeEvent(self, event):
        """
        Is called when the mainwindow gets resized.
        The elements on the right site of the window will be replaced.
        """
        window_width = self.size().width()
        button_width = self.button_width

        self.kitcar_form_group_box.move(window_width-button_width-20, 10)
        self.track_generator_form_group_box.move(window_width-button_width-20, 100)

        self.line_length.move(window_width-button_width-20, 230)

        self.line_button.move(window_width-button_width-20, 260)
        self.zebra_button.move(window_width-button_width-20, 290)
        self.blocked_area_button.move(window_width-button_width-20, 320)

        self.radius.move(window_width-button_width-20, 380)
        self.arc_length.move(window_width-button_width-20, 410)
        self.right_curve_button.move(window_width-button_width-20, 440)
        self.left_curve_button.move(window_width-button_width-20, 470)
        self.clothoid_button.move(window_width-button_width-20, 500)

        self.parking_area_button.move(window_width-button_width-20, 560)
        self.traffic_island_button.move(window_width-button_width-20, 590)
        self.intersection_button.move(window_width-button_width-20, 620)

    def save_python_button_clicked(self):
        """
        Asks the user for a directory.
        Calls the function python_writer.
        """
        if not len(self.road) > 1:
            QMessageBox.about(self, 'Warning', 'Es ist keine Strecke vorhanden!')
            return
        file, _ = QFileDialog.getSaveFileName(self, 'Geben Sie einen Speicherort an.','/opt/.ros/kitcar-gazebo-simulation/simulation/models/env_db','Python Files (*.py)')
        if file == '':
            return
        elif not file.endswith('.py'):
            # Append file type if not given
            file += '.py'
        close_loop = False
        if not self.road[-1]['end'] == self.start:
            mb = QMessageBox()
            ret = mb.question(self, '', 'Soll die Strecke geschlossen werden?', mb.Yes | mb.No)
            close_loop = True if ret == mb.Yes else False
        try:
            python_writer(self.road, file, close_loop)
            QMessageBox.about(self, 'Information', 'Die Strecke wurde gespeichert')
        except Exception as e:
            QMessageBox.about(self, 'Error', f'Die Strecke konnte nicht gespeichert werden.\nFehlermeldung:\n{e}')
        
    
    def load_python_button_clicked(self):
        """
        Asks the user for a python file.
        Trys to call the function python_reader.
        """
        file, _ = QFileDialog.getOpenFileName(self, 'Wählen Sie die Datei aus.','/opt/.ros/kitcar-gazebo-simulation/simulation/models/env_db','Python Files (*.py)')
        if file == '':
            return       
        try:
            python_reader(file, self)
            self.update_svg()
        except Exception as e:
            QMessageBox.about(self, 'Error', f'Die Strecke konnte nicht geladen werden.\nFehlermeldung:\n{e}')

    def save_xml_button_clicked(self):
        """
        Asks the user for a directory.
        Calls the function xml_writer.
        """
        if not len(self.road) > 1:
            QMessageBox.about(self, 'Warning', 'Es ist keine Strecke vorhanden!')
            return
        file, _ = QFileDialog.getSaveFileName(self, 'Geben Sie einen Speicherort an.','','XML Files (*.xml)')
        if file == '':
            return
        elif not file.endswith('.xml'):
            # Append file type if not given
            file += '.xml'

        xml_writer(self.road, file, self.factor)
        QMessageBox.about(self, 'Information', 'Die Strecke wurde gespeichert')
    
    def load_xml_button_clicked(self):
        """
        Asks the user for a xml file.
        Trys to call the function xml_reader.
        """
        file, _ = QFileDialog.getOpenFileName(self, 'Wählen Sie die Datei aus.','/opt/.ros/kitcar-gazebo-simulation/simulation/models/env_db','XML Files (*.xml)')
        if file == '':
            return       
        try:
            xml_reader(file, self)
            self.update_svg()
        except Exception as e:
            QMessageBox.about(self, 'Error', f'Die Strecke konnte nicht geladen werden.\nFehlermeldung:\n{e}')
    
    def line_button_clicked(self):
        """
        Insert a straigth element to the road.
        """
        if self.line_length.text():
            if float(self.line_length.text()) > 0:
                self.append_road_element(get_line_dict(self.road[-1]['end'] , self.road[-1]['endDirection'], float(self.line_length.text()), self.factor))
        
    def zebra_button_clicked(self):
        """
        Insert a zebra element to the road.
        """
        if self.line_length.text():
            if float(self.line_length.text()) > 0:
                self.append_road_element(get_zebra_dict(self.road[-1]['end'] , self.road[-1]['endDirection'], float(self.line_length.text()), self.factor))
        
    def blocked_area_button_clicked(self):
        """
        Insert a blocked element to the road.
        """
        if self.line_length.text():
            if float(self.line_length.text()) > 0:
                self.append_road_element(get_blocked_area_dict(self.road[-1]['end'] , self.road[-1]['endDirection'], float(self.line_length.text()), self.factor))
        
    def right_curve_button_clicked(self):
        """
        Insert a rigth curve element to the road.
        """
        if self.radius.text() and self.arc_length.text():
            if float(self.radius.text()) > 0 and float(self.arc_length.text()) > 0:
                self.append_road_element(get_right_curve_dict(self.road[-1]['end'] , self.road[-1]['endDirection'], float(self.radius.text()), float(self.arc_length.text()), self.factor))
       
    def left_curve_button_clicked(self):
        """
        Insert a left curve element to the road.
        """
        if self.radius.text() and self.arc_length.text():
            if float(self.radius.text()) > 0 and float(self.arc_length.text()) > 0:
                self.append_road_element(get_left_curve_dict(self.road[-1]['end'] , self.road[-1]['endDirection'], float(self.radius.text()), float(self.arc_length.text()), self.factor))
    
    def clothoid_button_clicked(self):
        """
        Open the clothoid window.
        """
        self.clothoid_window = clothoids_window.ClothoidWindow(self)
        self.clothoid_window.show()

    def parking_area_button_clicked(self):
        """
        Open the parking area window.
        """
        self.parking_area_window = parking_area.ParkingAreaWindow(self)
        self.parking_area_window.show()
    
    def traffic_island_button_clicked(self):
        """
        Open the traffic island window.
        """
        self.traffic_island_window = traffic_island.TrafficIslandWindow(self)
        self.traffic_island_window.show()
    
    def intersection_button_clicked(self):
        """
        Open the intersection window.
        """       
        self.intersection_window = intersection.IntersectionWindow(self)
        self.intersection_window.show()
        
    def delete_list_element(self):
        """
        Delete the selected element of the road
        """
        if self.list_widget.selectedItems():
            # Get index of the selected road element
            index = self.list_widget.currentRow()
            # Delete the road element in the listWidget
            self.list_widget.takeItem(index)
            # Delete the element in self.road
            self.road.pop(index+1)
            self.reconnect_road()
            self.update_coordinates()
            self.update_svg()
        else:
            QMessageBox.about(self, 'Waring', 'Es ist kein Streckenelement ausgewählt.')
    
    def reconnect_road(self):
        """
        Rebuild the whole road.
        All points will be calculated again.
        """
        self.open_intersections.clear()
        for idx, element in enumerate(self.road):
            # The first element in self.road has to be skipped
            if idx > 0:
                prev_element = self.road[idx-1]
                if element['name'] == 'line':
                    self.road[idx] = get_line_dict(prev_element['end'], prev_element['endDirection'], element['length'], self.factor)
                elif element['name'] == 'zebra':
                    self.road[idx] = get_zebra_dict(prev_element['end'], prev_element['endDirection'], element['length'], self.factor)
                elif element['name'] == 'blockedArea':
                    self.road[idx] = get_blocked_area_dict(prev_element['end'], prev_element['endDirection'], element['length'], self.factor)
                elif element['name'] == 'circleRight':
                    self.road[idx] = get_right_curve_dict(prev_element['end'], prev_element['endDirection'], element['radius'], element['arcLength'], self.factor)
                elif element['name'] == 'circleLeft':
                    self.road[idx] = get_left_curve_dict(prev_element['end'], prev_element['endDirection'], element['radius'], element['arcLength'], self.factor)
                elif element['name'] == 'parkingArea':
                    self.road[idx] = get_parking_area_dict(prev_element['end'], prev_element['endDirection'], element['length'], element['right'], element['left'], self.factor)
                elif element['name'] == 'trafficIsland':
                    self.road[idx] = get_traffic_island_dict(prev_element['end'], prev_element['endDirection'], element['zebraLength'], element['islandWidth'], element['curveAreaLength'], element['curvature'], self.factor)
                elif element['name'] == 'intersection':
                    self.road[idx] = get_intersection_dict(prev_element['end'], prev_element['endDirection'], element['text'], element['length'], self.open_intersections, self.factor)
                elif element['name'] == 'clothoid':
                    self.road[idx] = get_clothoid_dict(prev_element['end'], prev_element['endDirection'], element['a'], element['angle'], element['angleOffset'], element['type'], element['localEnd'], element['localDirection'])
                self.road[idx]['end'], self.road[idx]['endDirection'], self.road[idx]['skip_intersection'], self.road[idx]['intersection_radius'] = check_for_intersection_connection(self.road[idx]['end'], self.road[idx]['endDirection'], self.open_intersections)
                self.road[idx].update({'rightLine': element['rightLine'], 'middleLine': element['middleLine'], 'leftLine': element['leftLine']})
    
    def insert_list_name(self, name):
        """
        Insert a name to the listWidget
        """
        if name == 'line':
            self.list_widget.addItem('Gerade')
        elif name == 'zebra':
            self.list_widget.addItem('Zebrastreifen')
        elif name == 'blockedArea':
            self.list_widget.addItem('Hindernis')
        elif name == 'circleRight':
            self.list_widget.addItem('Rechts Kurve')
        elif name == 'circleLeft':
            self.list_widget.addItem('Links Kurve')
        elif name == 'clothoid':
            self.list_widget.addItem('Klothoid')
        elif name == 'parkingArea':
            self.list_widget.addItem('Parkplatz')
        elif name == 'trafficIsland':
            self.list_widget.addItem('Fußgängerinsel')
        elif name == 'intersection':
            self.list_widget.addItem('Kreuzung')
            
    def append_road_element(self, road_element, skip_svg=False):
        """
        Append an element to self.road
        """
        # If roadElement has no middleLine a window opens and asks for a line style.
        # A roadElement from the GUI will not have a middleLine.
        # A roadElement from a loaded file will already have a middleLine.
        if not 'middleLine' in road_element:
            line_style_window = select_line_style.SelectLineStyleWindow()
            line_style_window.exec_()
            road_element.update(line_style_window.get_value())
        road_element['end'], road_element['endDirection'], road_element['skip_intersection'], road_element['intersection_radius'] = check_for_intersection_connection(road_element['end'], road_element['endDirection'], self.open_intersections)
        # Update the end coordinates and direction
        self.road.append(road_element)
        self.update_coordinates()
        self.insert_list_name(road_element['name'])
        if not skip_svg:
            self.update_svg()
    
    def update_svg(self):
        """
        Generate xml file.
        Generate svg file with track generator.
        Open window with svg file.
        Delete the generated files.
        """
        os.makedirs(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp'))
        xml_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp', 'temp.xml')
        svg_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp')
        try:
            xml_writer(self.road, xml_path, self.factor)
            generate_track([xml_path], svg_path, False, False)
            self.svg_widget.load_svg(os.path.join(svg_path, 'temp', 'temp.svg'))
        except Exception as e:
            QMessageBox.about(self, 'Error', f'Die Vorschau konnte nicht erstellt werden.\nFehlermeldung:\n{e}')
        shutil.rmtree(svg_path)
    
    def update_coordinates(self):
        """
        Update the end coordinates and direction
        """
        self.end_label.setText(f'x: {round(self.road[-1]["end"][0]/self.factor, 2)}, y: {-round(self.road[-1]["end"][1]/self.factor, 2)}')
        self.direction_label.setText(f'{self.road[-1]["endDirection"]%360}°')       

    def wheelEvent(self, event):
        """
        Is called if mouse wheel is used
        """
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()

        elif delta < 0:
            self.zoom_out()
    
    @QtCore.pyqtSlot()
    def zoom_in(self):
        """
        Is called from mouse wheel or plus button
        """
        scale_tr = QTransform()
        scale_tr.scale(1.5, 1.5)
        tr = self.view.transform() * scale_tr
        self.view.setTransform(tr)

    @QtCore.pyqtSlot()
    def zoom_out(self):
        """
        Is called from mouse wheel os minus button
        """
        scale_tr = QTransform()
        scale_tr.scale(1.5, 1.5)
        scale_inverted, invertible = scale_tr.inverted()
        if invertible:
            tr = self.view.transform() * scale_inverted
            self.view.setTransform(tr)

