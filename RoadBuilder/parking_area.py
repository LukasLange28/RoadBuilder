import math

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QComboBox, QTreeWidgetItem, QTreeWidget, QMessageBox,  QFormLayout, QGroupBox
from PyQt5.QtGui import QPainter, QPen, QFont, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QPoint, QLineF

from get_road_element_dict import get_parking_area_dict, get_int

class ParkingAreaWindow(QWidget):
    
    def __init__(self, parent_window):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        font = QFont('Roboto', 10)
        self.setFont(font)

        self.setWindowTitle('Parkbereich einfügen')
        self.resize(1600,500)
        
        self.parent_window =parent_window
        self.factor = parent_window.factor
        self.parking_dict = {'left': [], 'right': [], 'name': 'parkingArea'}
        
        self.road = parent_window.road
        self.parking_spot_size = [[0.7, 0.3], [0.3, 0.5]]
        
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(['Parkplatz','Belegung'])
        self.tree.header().setDefaultSectionSize(125)
        self.tree.setMinimumSize(250,400)
        self.tree.expandAll()
        
        self.delete_parking_spot_button = QPushButton('Löschen', self)
        self.delete_parking_spot_button.clicked.connect(self.delete_parking_spot)
        self.delete_parking_spot_button.move(0, 410)
        self.delete_parking_spot_button.setFixedWidth(200)
        
        self.finish_button = QPushButton('Fertig',self)
        self.finish_button.clicked.connect(self.finish_button_clicked)
        self.finish_button.move(0, 440)
        self.finish_button.setFixedWidth(200)
        
        self.line_length = QLineEdit(self)
        self.line_length.setToolTip('Länge des Parkbereichs')
        self.line_length.setText('5')
        self.line_length.setPlaceholderText('Länge')
        self.line_length.setFixedWidth(150)
        self.line_length.setValidator(QtGui.QDoubleValidator())
        self.line_length.textChanged.connect(self.update_length)
        self.parking_dict['length'] = float(self.line_length.text())
        
        self.park_start = QLineEdit(self)
        self.park_start.setToolTip('Startpunkt des Parkplatzes')
        self.park_start.setPlaceholderText('Start')
        self.park_start.setFixedWidth(150)
        self.park_start.setValidator(QtGui.QDoubleValidator())
        
        self.number_of_parking_spots = QLineEdit(self)
        self.number_of_parking_spots.setToolTip('Anzahl der Parkspots')
        self.number_of_parking_spots.setPlaceholderText('Anzahl')
        self.number_of_parking_spots.setFixedWidth(150)
        self.number_of_parking_spots.setValidator(QtGui.QIntValidator())
        
        self.parking_spot_site = QComboBox(self)
        self.parking_spot_site.addItems(('Links', 'Rechts'))
        self.parking_spot_site.setFixedWidth(150)
        
        self.parking_spot_type = QComboBox(self)
        self.parking_spot_type.addItems(('Längs', 'Quer'))
        self.parking_spot_type.setFixedWidth(150)

        form = QFormLayout()
        form.addRow(QLabel('Gesamtlänge:'), self.line_length)
        form.addRow(QLabel('Parkplätze:'))
        form.addRow(QLabel('Parkplatzanfang:'), self.park_start)
        form.addRow(QLabel('Anzahl der Parkplätze:'), self.number_of_parking_spots)
        form.addRow(QLabel('Seite:'), self.parking_spot_site)
        form.addRow(QLabel('Ausrichtung:'), self.parking_spot_type)
        form.setVerticalSpacing(0)
        
        self.form_group_box = QGroupBox(self)
        self.form_group_box.setLayout(form)
        self.form_group_box.setMinimumSize(340,150)
        self.form_group_box.move(250,-20)
        
        self.add_parking_spot = QPushButton('Einfügen', self)
        self.add_parking_spot.clicked.connect(self.add_parking_spot_clicked)
        self.add_parking_spot.move(590, 0)
        self.add_parking_spot.resize(100, 130)
        
    def paintEvent(self, event):
        road_width = 75
        start = [300, 300]
        length = self.parking_dict['length']
        angle = 0
        end = [start[0]+length*self.factor + 10, start[0]]

        painter = QPainter(self)     
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.gray, road_width, cap=Qt.FlatCap))
        # Road of the parking area
        painter.drawLine(QLineF(start[0], start[1], end[0], end[1],))
        # Smaller pen for the parking lines
        painter.setPen(QPen(Qt.gray, 10, cap=Qt.FlatCap))
        points = []
        path = QPainterPath()
        polygon = []

        for dict in self.parking_dict['right']:
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
            p = [QPoint(i[0],i[1]) for i in points]
            polygon.append(QPolygonF(p))
            
        for dict in self.parking_dict['left']:
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
            p = [QPoint(i[0],i[1]) for i in points]
            polygon.append(QPolygonF(p))
        
        for poly in polygon:
            path.addPolygon(poly)
            painter.drawPath(path)
    
    def finish_button_clicked(self):
        self.hide() 
        if self.parking_dict['left'] or self.parking_dict['right']:
            self.parent_window.append_road_element(get_parking_area_dict(self.road[-1]['end'], self.road[-1]['endDirection'], self.parking_dict['length'], self.parking_dict['right'], self.parking_dict['left'], self.factor))
            self.parent_window.update()
            del self
        
    def add_parking_spot_clicked(self):
        """
        Creat new dictionary for new spot.
        Check if the new spot fits into the parking area.
        Insert the spot into the parking area.
        """
        site = 'left' if self.parking_spot_site.currentText() == 'Links' else 'right'
        if self.park_start.text() and self.number_of_parking_spots.text():
            if float(self.park_start.text()) >= 0 and float(self.number_of_parking_spots.text()) > 0:
                dict = {}
                dict['start'] = float(self.park_start.text())
                dict['number'] = get_int(float(self.number_of_parking_spots.text()))
                dict['type'] = self.parking_spot_type.currentIndex()
                dict['spots'] = ['FREE']* dict['number']
                # Checks if the new parkingspot is overlapping with the existing Parkingspots
                new_end = dict['start'] + dict['number'] * self.parking_spot_size[dict['type']][0] + 2 * self.parking_spot_size[dict['type']][1]
                for spots in self.parking_dict[site]:
                    existing_end = spots['start'] + spots['number'] * self.parking_spot_size[spots['type']][0] + 2 * self.parking_spot_size[spots['type']][1]
                    if (dict['start'] >= spots['start'] and dict['start'] <= existing_end):
                        QMessageBox.about(self, 'Warning', 'Die Parkbuchten überschneiden sich!')
                        return
                    elif (new_end >= spots['start'] and new_end <= existing_end):
                        QMessageBox.about(self, 'Warning', 'Die Parkbuchten überschneiden sich!')
                        return
                if new_end >= self.parking_dict['length']:
                    QMessageBox.about(self, 'Warning', 'Die Parkbuchten überschreiten die Gesamtlänge')
                    return
               
                # Insert the spot into the tree
                parent = QTreeWidgetItem(self.tree)
                dict['parent'] = parent
                parent.setText(0, self.parking_spot_site.currentText())
                for x in range(dict['number']):
                    child = QTreeWidgetItem(parent)
                    child.setText(0, f'Parkplatz {x}')
                    combo = QComboBox(self)
                    combo.addItems(('Frei', 'Blockiert', 'Besetzt'))
                    combo.activated.connect(lambda _, a=x: self.change_spot_value(a, dict))
                    self.tree.setItemWidget(child,1,combo)
                self.tree.expandItem(parent)
                # Insert the spot into the parkingDict
                self.parking_dict[site].append(dict)
                self.update()
    
    def delete_parking_spot(self):
        """
        Delete the spot of selected tree element.
        """
        item = self.tree.currentItem()
        text = item.text(0)
        if text.startswith('Parkplatz '):
            # parking bay
            number = self.tree.indexOfTopLevelItem(item.parent())
            site = 'left' if item.parent().text(0).startswith('Links') else 'right'
            for park in self.parking_dict[site]:
                if park['parent'] == item.parent():
                    park['number'] -= 1
                    parent = item.parent()
                    parent.removeChild(item)
                    for x in range(park['number']):
                        parent.child(x).setText(0, f'Parkplatz {x}')
                    if park['number'] == 0:
                        # Delete parking spot if there are no bay's
                        self.tree.takeTopLevelItem(number)
                        self.parking_dict[site].pop(self.parking_dict[site].index(park)) 

        elif text.startswith('Links') or text.startswith('Rechts'):
            # parking spot
            index = self.tree.currentIndex()
            number = index.row()
            site = 'left' if text.startswith('Links') else 'right'
            for park in self.parking_dict[site]:
                if park['parent'] == item:
                    self.parking_dict[site].remove(park)
             
            self.tree.takeTopLevelItem(number)
            
        self.update()
    
    def change_spot_value(self, idx, park):
        """
        If the state of a parking bay is changed this function will be called.
        The park['spots'][idx] will be chenged to the parking bay state.
        """
        text = self.tree.itemWidget(self.tree.currentItem(), 1).currentText()
        if text == 'Frei':
            park['spots'][idx] = 'FREE' 
        elif text == 'Blockiert':
            park['spots'][idx] = 'BLOCKED' 
        else:
            park['spots'][idx] = 'OCCUPIED'
        
        
    def update_length(self):
        """
        Will be called if the length of the parking area id changed.
        Change self.parkingDict['length'] to the value of the line edit.
        """
        if self.line_length.text():
            self.parking_dict['length'] = float(self.line_length.text())
            self.update()
        