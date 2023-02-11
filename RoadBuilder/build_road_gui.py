import sys
import math

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QMessageBox, QFileDialog, QFormLayout, QGroupBox, QShortcut, QWidget
from PyQt5.QtGui import QPainter, QPen, QFont, QPainterPath, QPolygonF, QTransform, QKeySequence
from PyQt5.QtCore import Qt, QPoint, QLineF

if  not '/home/id305564/Schreibtisch/U/track_generator' in sys.path:
    sys.path.append('/home/id305564/Schreibtisch/U/track_generator')

import clothoids_window, parking_area, traffic_island, intersection, select_line_style
from get_road_element_dict import *
from python_writer_reader import python_reader, python_writer
from xml_writer_reader import xml_writer, xml_reader
from preview_window import xml_preview



class Window(QMainWindow):
    
    def __init__(self):
        
        super().__init__()       

        self.move_window = QPoint(-10000,-10000)
        
        # Road position
        self.start = [10000, 10000]
        self.end = [10000, 10000]
        self.direction = 0

        # One meter = 100 pixel
        self.factor = 100
        # Different parking spot sizes
        self.parking_spot_size = [[0.7, 0.3], [0.3, 0.5]]
        
        # road list
        self.road = []
        self.road.append({'name': 'firstElement', 'start': self.start, 'end': self.end, 'direction': self.direction, 'endDirection': self.direction})
        
        # list for open intersection ends
        self.open_intersections = []
        
        # creates widget for road presentation
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = QtWidgets.QGraphicsView(self.scene)
        self.paint_road = PaintRoad(self.road, self.move_window, self.factor, self.parking_spot_size, self)
        self.paint_road.setFixedSize(20000, 20000)
        self.paint_road.move(-10000,-10000)
        self.scene.addWidget(self.paint_road)
        self.setCentralWidget(self.view)

        # creates shortcuts
        QShortcut(QKeySequence(QtCore.Qt.Key_Minus), self.view, context=QtCore.Qt.WidgetShortcut, activated=self.zoom_out)
        QShortcut(QKeySequence(QtCore.Qt.Key_Plus), self.view, context=QtCore.Qt.WidgetShortcut, activated=self.zoom_in)

        self.setWindowTitle("RoadBuilder")
        font = QFont('Roboto', 10)
        self.setFont(font)

        screen_width = QtWidgets.QDesktopWidget().screenGeometry(-1).width()
        button_width = 180
        self.button_width = button_width
        
        # graphic elements
        self.end_label = QLabel(f'x: {self.road[-1]["end"][0]/self.factor-100}, y: {self.road[-1]["end"][1]/self.factor-100}')
        self.direction_label = QLabel(f'{self.road[-1]["endDirection"]%360}°')

        form = QFormLayout()
        form.setVerticalSpacing(0)
        form.addRow(QLabel('Start:'), QLabel(f'x: {self.start[0]/self.factor-100}, y: {self.start[1]/self.factor-100}'))
        form.addRow(QLabel('Ende:'), self.end_label)
        form.addRow(QLabel('Richtung:'), self.direction_label)

        self.form_group_box = QGroupBox(self)
        self.form_group_box.setLayout(form)
        self.form_group_box.setMinimumSize(200,100)
        self.form_group_box.move(200, 0)

        self.list_widget= QtWidgets.QListWidget(self)
        self.list_widget.resize(200, 300)
        self.list_widget.setWindowTitle('Strecke')
        self.list_widget.setToolTip('Hier erscheinen die Streckenabschnitte')
        self.list_widget.move(0, 20)
        
        self.line_button = QPushButton('Streckenelement löschen', self)
        self.line_button.setToolTip('Das ausgewählte Element wird gelöscht')
        self.line_button.move(0, 320)
        self.line_button.clicked.connect(self.delete_list_element)
        self.line_button.setFixedWidth(200)
        
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
        
        xml_preview_button = QPushButton('Vorschau', self)
        xml_preview_button.setToolTip('Erzeugt eine Vorschau der SVG Datei')
        xml_preview_button.move(screen_width-button_width-20, 70)
        xml_preview_button.clicked.connect(self.xml_preview_button_clicked)
        xml_preview_button.setFixedWidth(156)
        
        track_generator_form = QFormLayout()
        track_generator_form.setVerticalSpacing(0)
        track_generator_form.addRow(QLabel('Track Generator:'))
        track_generator_form.addRow(save_xml_button, load_xml_button)
        track_generator_form.addRow(xml_preview_button)

        self.track_generator_form_group_box = QGroupBox(self)
        self.track_generator_form_group_box.setLayout(track_generator_form)
        self.track_generator_form_group_box.setMinimumSize(180, 100)
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
        
        self.clothoid_button = QPushButton('Klothoid einfügen', self)
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
        python_writer(self.road, file, close_loop)
        QMessageBox.about(self, 'Information', 'Die Strecke wurde gespeichert')
    
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
            self.paint_road.update()
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
            self.paint_road.update()
        except Exception as e:
            QMessageBox.about(self, 'Error', f'Die Strecke konnte nicht geladen werden.\nFehlermeldung:\n{e}')
    
    def xml_preview_button_clicked(self):
        if not len(self.road) > 1:
            QMessageBox.about(self, 'Warning', 'Es ist keine Strecke vorhanden!')
            return
        xml_preview(self)
    
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
            self.reconnect_road(index-1)
            self.update_coordinates()
            self.paint_road.update()
        else:
            QMessageBox.about(self, 'Waring', 'Es ist kein Streckenelement ausgewählt.')
    
    def reconnect_road(self, index):
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
                    self.road[idx] = get_clothoid_dict(prev_element['end'], prev_element['endDirection'], element['a'], element['angle'], element['angleOffset'], element['type'], element['points'])
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
            
    def append_road_element(self, road_element):
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
    
    def update_coordinates(self):
        """
        Update the end coordinates and direction
        """
        self.end_label.setText(f'x: {round(self.road[-1]["end"][0]/self.factor-100, 2)}, y: {round(self.road[-1]["end"][1]/self.factor-100, 2)}')
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

class PaintRoad(QWidget):
    def __init__(self, road, move_window, factor, parking_spot_size, parent_window):
        super().__init__()
        self.road = road
        self.move_window = move_window
        self.factor = factor
        self.parking_spot_size = parking_spot_size
        self.parent_window = parent_window

        self.container_widget = QWidget()

        self.mouse_pos = QPoint(0, 0)
        self.cursor_start = QPoint(0, 0)
        
    def wheelEvent(self, event):
        """
        Is called if mouse wheel is used
        """
        delta = event.angleDelta().y()
        if delta > 0:
            self.parent_window.zoom_in()

        elif delta < 0:
            self.parent_window.zoom_out()
    
    def mousePressEvent(self, event):
        """
        Is calles if left mouse button is clicked
        """
        self.cursor_start = self.container_widget.cursor().pos()
        print(self.cursor_start)
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """
        Is calles if left mouse button is clicked and mouse moves
        """
        delta = self.cursor_start - self.container_widget.cursor().pos()
        
        # panning area
        if event.buttons() == Qt.LeftButton:

            self.move(self.parent_window.move_window.x() - delta.x(), self.parent_window.move_window.y() - delta.y())

        self.mouse_pos = event.localPos()

    def mouseReleaseEvent(self, event):
        """
        Is calles if left mouse button is released
        """
        self.unsetCursor()
        self.mouse_pos = event.localPos()
        self.parent_window.move_window.setX(self.parent_window.move_window.x() - (self.cursor_start - self.container_widget.cursor().pos()).x())
        self.parent_window.move_window.setY(self.parent_window.move_window.y() - (self.cursor_start - self.container_widget.cursor().pos()).y())

    def paintEvent(self, event):
        """
        This function is called automaticly.
        It paints the road.
        """
        road_width = 75
        painter = QPainter(self)     
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.gray, road_width, cap=Qt.FlatCap))
        
        for element in self.road:
            if element['name'] == 'line':
                painter.drawLine(element['start'][0] , element['start'][1] , element['end'][0] , element['end'][1] )
            
            if element['name'] == 'zebra':
                painter.drawLine(element['start'][0] , element['start'][1] , element['end'][0] , element['end'][1] )
                painter.setPen(QPen(Qt.white, road_width/10, cap=Qt.FlatCap))
                angle = math.radians(element['direction'])
                # Draw the white zebra lines
                for x in range(5):
                    painter.drawLine(get_int(element['start'][0]  + ((4*road_width - 2*road_width*x)/10)*math.sin(angle)),get_int( element['start'][1]  + ((4*road_width - 2*road_width*x)/10)*math.cos(angle)), get_int(element['end'][0] + ((4*road_width - 2*road_width*x)/10)*math.sin(angle)),get_int( element['end'][1] + ((4*road_width - 2*road_width*x)/10)*math.cos(angle)))
                painter.setPen(QPen(Qt.gray, road_width, cap=Qt.FlatCap))
            
            if element['name'] == 'blockedArea':
                painter.drawLine(element['start'][0] , element['start'][1] , element['end'][0] , element['end'][1])
                painter.setPen(QPen(Qt.black, road_width/2, cap=Qt.FlatCap))
                angle = math.radians(element['direction'])
                # Draw the black obstacle
                painter.drawLine(get_int(element['start'][0] + road_width/4*math.sin(angle)), get_int(element['start'][1] + road_width/4*math.cos(angle)), get_int(element['end'][0] + road_width/4*math.sin(angle)), get_int(element['end'][1] + road_width/4*math.cos(angle)))
                painter.setPen(QPen(Qt.gray, road_width, cap=Qt.FlatCap))
            
            if (element['name'] == 'circleRight') | (element['name'] == 'circleLeft'):
                # Draw the curves.
                # The startpoints for drawArc are not the startpoints of the curve.
                
                height = get_int(element['radius'] *2 * self.factor)
                width = get_int(element['radius'] *2 * self.factor)
                start_x = element['start'][0]
                start_y = element['start'][1]

                a = element['a']
                arc_length = element['arcLength']*16
                painter.drawArc(start_x, start_y, width, height, a, arc_length)
            
            if element['name'] == 'clothoid':
                path = QPainterPath()
                polygon = []
                start = element['start']
                radian = math.radians(element['direction'])
                #[get_int(d[0]*math.cos(radian)+d[1]*math.sin(radian)), get_int(d[0]*math.sin(radian)-d[1]*math.cos(radian))]
                p = [QPoint(get_int(i[0]*math.cos(radian) + i[1]*math.sin(radian))+start[0], get_int(-i[0]*math.sin(radian) + i[1]*math.cos(radian))+start[1]) for i in element['points']]
                #p = [QPoint((i[0]+start[0]), (i[1]+start[1])) for i in element['points']]
                polygon = QPolygonF(p)
                path.addPolygon(polygon)
                painter.drawPath(path)

            if element['name'] == 'trafficIsland':
                points = []
                polygon = []
                angle = math.radians(element['direction'])
                
                # Right
                points.append([get_int(element['start'][0] + road_width/4*math.sin(angle)), get_int(element['start'][1] + road_width/4*math.cos(angle))])
                # -
                points.append([get_int(points[-1][0] + element['curveAreaLength']*self.factor/2*math.cos(angle)), get_int(points[-1][1] - element['curveAreaLength']*self.factor/2*math.sin(angle))])
                start_of_island = [get_int(points[-1][0] + element['curveAreaLength']*self.factor/2*math.cos(angle)), get_int(points[-1][1] - element['curveAreaLength']*self.factor/2*math.sin(angle))]
                # \
                points.append([get_int(start_of_island[0] + element['islandWidth']/2*self.factor*math.sin(angle)), get_int(start_of_island[1] + element['islandWidth']/2*self.factor*math.cos(angle))])
                # -
                points.append([get_int(points[-1][0] + element['zebraLength']*self.factor*math.cos(angle)), get_int(points[-1][1] - element['zebraLength']*self.factor*math.sin(angle))])
                end_of_island = [get_int(points[-1][0] - element['islandWidth']/2*self.factor*math.sin(angle)), get_int(points[-1][1] - element['islandWidth']/2*self.factor*math.cos(angle))]
                # /
                points.append([get_int(end_of_island[0] + element['curveAreaLength']/2*self.factor*math.cos(angle)), get_int(end_of_island[1] - element['curveAreaLength']/2*self.factor*math.sin(angle))])
                # -
                points.append([get_int(points[-1][0] + element['curveAreaLength']*self.factor/2*math.cos(angle)), get_int(points[-1][1] - element['curveAreaLength']*self.factor/2*math.sin(angle))])
                
                p = [QPoint(i[0], i[1]) for i in points]
                polygon.append(QPolygonF(p))
                points.clear()
                
                # Left
                points.append([get_int(element['start'][0] - road_width/4*math.sin(angle)), get_int(element['start'][1] - road_width/4*math.cos(angle))])
                # -
                points.append([get_int(points[-1][0] + element['curveAreaLength']*self.factor/2*math.cos(angle)), get_int(points[-1][1] - element['curveAreaLength']*self.factor/2*math.sin(angle))])
                start_of_island = [get_int(points[-1][0] + element['curveAreaLength']*self.factor/2*math.cos(angle)), get_int(points[-1][1] - element['curveAreaLength']*self.factor/2*math.sin(angle))]
                # /
                points.append([get_int(start_of_island[0] - element['islandWidth']/2*self.factor*math.sin(angle)), get_int(start_of_island[1] - element['islandWidth']/2*self.factor*math.cos(angle))])
                # -
                points.append([get_int(points[-1][0] + element['zebraLength']*self.factor*math.cos(angle)), get_int(points[-1][1] - element['zebraLength']*self.factor*math.sin(angle))])
                end_of_island = [get_int(points[-1][0] + element['islandWidth']/2*self.factor*math.sin(angle)), get_int(points[-1][1] + element['islandWidth']/2*self.factor*math.cos(angle))]
                # \
                points.append([get_int(end_of_island[0] + element['curveAreaLength']/2*self.factor*math.cos(angle)), get_int(end_of_island[1] - element['curveAreaLength']/2*self.factor*math.sin(angle))])
                # -
                points.append([get_int(points[-1][0] + element['curveAreaLength']*self.factor/2*math.cos(angle)), get_int(points[-1][1] - element['curveAreaLength']*self.factor/2*math.sin(angle))])
                
                p = [QPoint(i[0], i[1]) for i in points]
                polygon.append(QPolygonF(p))
                
                painter.setPen(QPen(Qt.gray, road_width/2, cap=Qt.FlatCap))
                path = QPainterPath()
                for poly in polygon:
                    path.addPolygon(poly)
                    painter.drawPath(path)
                painter.setPen(QPen(Qt.gray, road_width, cap=Qt.FlatCap))
                    
            if element['name'] == 'intersection':
                points = []
                angle = math.radians(element['direction'])
                arm_length = get_int(element['length']/2*self.factor)
                points.append([get_int(element['start'][0]+(arm_length*math.cos(angle))), get_int(element['start'][1]-(arm_length*math.sin(angle)))])
                middle_point = points[-1]
                # Back
                points.append([get_int(middle_point[0]-(arm_length*math.cos(angle))), get_int(middle_point[1]+(arm_length*math.sin(angle)))])
                points.append(middle_point)
                # Left              
                points.append([get_int(middle_point[0]-(arm_length*math.sin(angle))), get_int(middle_point[1]-(arm_length*math.cos(angle)))])
                points.append(middle_point)
                # Top
                points.append([get_int(middle_point[0]+(arm_length*math.cos(angle))), get_int(middle_point[1]-(arm_length*math.sin(angle)))])
                points.append(middle_point)
                # Right
                points.append([get_int(middle_point[0]+(arm_length*math.sin(angle))), get_int(middle_point[1]+(arm_length*math.cos(angle)))])
                points.append(middle_point)
                
                p = [QPoint(i[0], i[1]) for i in points]
                polygon = QPolygonF(p)
                
                path = QPainterPath()                
                path.addPolygon(polygon)
                painter.drawPath(path)
            
            if element['name'] == 'parkingArea':
                start = element['start']
                angle = math.radians(element['direction'])
                
                painter.drawLine(QLineF(element['start'][0], element['start'][1], element['end'][0], element['end'][1]))
                painter.setPen(QPen(Qt.gray, 10, cap=Qt.FlatCap))
                points = []
                path = QPainterPath()
                polygon = []

                for dict in element['right']:
                    spot_length = self.parking_spot_size[dict['type']][0]*self.factor
                    spot_heigth = self.parking_spot_size[dict['type']][1]*self.factor
                    points = []
                    points.append([get_int(start[0] + ((dict['start']*self.factor+5)*math.cos(angle))), get_int(start[1] - ((dict['start']*self.factor+5)*math.sin(angle)))])
                    # |
                    points.append([get_int(points[-1][0] + (road_width/2*math.sin(angle))), get_int(points[-1][1] + (road_width/2*math.cos(angle)))])
                    point = [get_int(points[-1][0] + (spot_heigth*math.cos(angle))), get_int(points[-1][1] - (spot_heigth*math.sin(angle)))]
                    # \
                    points.append([get_int(point[0] + (spot_heigth*math.sin(angle))), get_int(point[1] + (spot_heigth*math.cos(angle)))])
                    # -
                    points.append([get_int(points[-1][0] + (dict['number'] * spot_length*math.cos(angle))), get_int(points[-1][1] - (dict['number'] * spot_length*math.sin(angle)))])
                    point = [get_int(points[-1][0] - (spot_heigth*math.sin(angle))), get_int(points[-1][1] - (spot_heigth*math.cos(angle)))]
                    # /
                    points.append([get_int(point[0] + (spot_heigth*math.cos(angle))), get_int(point[1] - (spot_heigth*math.sin(angle)))])
                    # |
                    points.append([get_int(points[-1][0] - (road_width/2*math.sin(angle))), get_int(points[-1][1] - (road_width/2*math.cos(angle)))])
                    p = [QPoint(i[0], i[1]) for i in points]
                    polygon.append(QPolygonF(p))
                    
                for dict in element['left']:
                    spot_length = self.parking_spot_size[dict['type']][0]*self.factor
                    spot_heigth = self.parking_spot_size[dict['type']][1]*self.factor
                    points = []
                    points.append([get_int(start[0] + ((dict['start']*self.factor+5)*math.cos(angle))), get_int(start[1] - ((dict['start']*self.factor+5)*math.sin(angle)))])
                    # |
                    points.append([get_int(points[-1][0] - (road_width/2*math.sin(angle))), get_int(points[-1][1] - (road_width/2*math.cos(angle)))])
                    point = [get_int(points[-1][0] + (spot_heigth*math.cos(angle))), get_int(points[-1][1] - (spot_heigth*math.sin(angle)))]
                    # /
                    points.append([get_int(point[0] - (spot_heigth*math.sin(angle))), get_int(point[1] - (spot_heigth*math.cos(angle)))])
                    # -
                    points.append([get_int(points[-1][0] + (dict['number'] * spot_length*math.cos(angle))), get_int(points[-1][1] - (dict['number'] * spot_length*math.sin(angle)))])
                    point = [get_int(points[-1][0] + (spot_heigth*math.sin(angle))), get_int(points[-1][1] + (spot_heigth*math.cos(angle)))]
                    # \
                    points.append([get_int(point[0] + (spot_heigth*math.cos(angle))), get_int(point[1] - (spot_heigth*math.sin(angle)))])
                    # |
                    points.append([get_int(points[-1][0] + (road_width/2*math.sin(angle))), get_int(points[-1][1] + (road_width/2*math.cos(angle)))])
                    p = [QPoint(i[0], i[1]) for i in points]
                    polygon.append(QPolygonF(p))
                
                for poly in polygon:
                    path.addPolygon(poly)
                    painter.drawPath(path)
                        
                painter.setPen(QPen(Qt.gray, road_width, cap=Qt.FlatCap))

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec())
