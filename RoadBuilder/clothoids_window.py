import math

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QComboBox, QFormLayout, QShortcut, QGraphicsScene, QGraphicsView, QMainWindow, QTabWidget
from PyQt5.QtGui import QPainter, QPen, QFont, QPainterPath, QPolygonF, QTransform, QKeySequence
from PyQt5.QtCore import Qt, QPoint

from RoadBuilder.get_road_element_dict import get_clothoid_dict, get_int, get_faculty, move_point, rotate_point

class ClothoidWindow(QMainWindow):
    
    def __init__(self, parent_window):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        font = QFont('Roboto', 10)
        self.setFont(font)

        self.setWindowTitle('Klothoide einfügen')
        self.resize(1200,800)
        
        self.parent_window =parent_window
        self.factor = parent_window.factor
        self.road = parent_window.road
        self.dict = {'a': 0, 'angle': 0, 'points': [], 'end': [0,0]}
        self.move_window = QPoint(-10000,-10000)
        self.start = [10000, 10000]

        scene = QGraphicsScene(self)
        self.view = QGraphicsView(scene)
        paint_clothoid = PaintClothoid(self.dict, self.move_window, self.factor, self)
        paint_clothoid.setFixedSize(20000, 20000)
        paint_clothoid.move(-10000,-10000)
        scene.addWidget(paint_clothoid)
        self.setCentralWidget(self.view)

        # creates shortcuts
        QShortcut(QKeySequence(QtCore.Qt.Key_Minus), self.view, context=QtCore.Qt.WidgetShortcut, activated=self.zoom_out)
        QShortcut(QKeySequence(QtCore.Qt.Key_Plus), self.view, context=QtCore.Qt.WidgetShortcut, activated=self.zoom_in)
        
        # Widgets for tab_a
        self.a = QLineEdit(self)
        self.a.setToolTip('Beeinflusst die Größe der Klothoide')
        self.a.setText('2')
        self.a.setPlaceholderText('A')
        self.a.setFixedWidth(120)
        self.a.setValidator(QtGui.QDoubleValidator())
        self.a.textChanged.connect(self.update_a_clothoid)

        self.arc_length_a = QLineEdit(self)
        self.arc_length_a.setToolTip('Winkel der Klothoide')
        self.arc_length_a.setText('180')
        self.arc_length_a.setPlaceholderText('Winkel')
        self.arc_length_a.setFixedWidth(120)
        self.arc_length_a.setValidator(QtGui.QDoubleValidator())
        self.arc_length_a.textChanged.connect(self.update_a_clothoid)

        self.direction_a = QComboBox(self)
        self.direction_a.addItems(('Rechts', 'Links'))
        self.direction_a.setFixedWidth(120)
        self.direction_a.activated[str].connect(self.update_a_clothoid)

        self.type_a = QComboBox(self)
        self.type_a.addItems(('Schließend', 'Öffnend'))
        self.type_a.setFixedWidth(120)
        self.type_a.activated[str].connect(self.update_a_clothoid)
      
        form_a = QFormLayout()
        form_a.addRow(QLabel('A:'), self.a)
        form_a.addRow(QLabel('Winkel:'), self.arc_length_a)
        form_a.addRow(QLabel('Richtung:'), self.direction_a)
        form_a.addRow(QLabel('Art:'), self.type_a)
        form_a.setVerticalSpacing(0)
        
        # Widgets for tab_end_radius
        self.end_radius = QLineEdit(self)
        self.end_radius.setToolTip('Radius am Ende der Kurve')
        self.end_radius.setText('1')
        self.end_radius.setPlaceholderText('Radius')
        self.end_radius.setFixedWidth(120)
        self.end_radius.setValidator(QtGui.QDoubleValidator())
        self.end_radius.textChanged.connect(self.update_end_radius_clothoid)

        self.arc_length_end_radius = QLineEdit(self)
        self.arc_length_end_radius.setToolTip('Winkel der Klothoide')
        self.arc_length_end_radius.setText('180')
        self.arc_length_end_radius.setPlaceholderText('Winkel')
        self.arc_length_end_radius.setFixedWidth(120)
        self.arc_length_end_radius.setValidator(QtGui.QDoubleValidator())
        self.arc_length_end_radius.textChanged.connect(self.update_end_radius_clothoid)

        self.direction_end_radius = QComboBox(self)
        self.direction_end_radius.addItems(('Rechts', 'Links'))
        self.direction_end_radius.setFixedWidth(120)
        self.direction_end_radius.activated[str].connect(self.update_end_radius_clothoid)

        self.type_end_radius = QComboBox(self)
        self.type_end_radius.addItems(('Schließend', 'Öffnend'))
        self.type_end_radius.setFixedWidth(120)
        self.type_end_radius.activated[str].connect(self.update_end_radius_clothoid)
      
        form_end_radius = QFormLayout()
        form_end_radius.addRow(QLabel('Kleinster Radius:'), self.end_radius)
        form_end_radius.addRow(QLabel('Winkel:'), self.arc_length_end_radius)
        form_end_radius.addRow(QLabel('Richtung:'), self.direction_end_radius)
        form_end_radius.addRow(QLabel('Art:'), self.type_end_radius)
        form_end_radius.setVerticalSpacing(0)
        
        # Widgets for tab_two_radii
        self.first_radius = QLineEdit(self)
        self.first_radius.setToolTip('Radius bei Kurvenstart')
        self.first_radius.setText('2')
        self.first_radius.setPlaceholderText('Anfangsradius')
        self.first_radius.setFixedWidth(120)
        self.first_radius.setValidator(QtGui.QDoubleValidator())
        self.first_radius.textChanged.connect(self.update_two_radii_clothoid)

        self.second_radius = QLineEdit(self)
        self.second_radius.setToolTip('Radius bei Kurvenende')
        self.second_radius.setText('1')
        self.second_radius.setPlaceholderText('Anfangsradius')
        self.second_radius.setFixedWidth(120)
        self.second_radius.setValidator(QtGui.QDoubleValidator())
        self.second_radius.textChanged.connect(self.update_two_radii_clothoid)

        self.arc_length_two_radii = QLineEdit(self)
        self.arc_length_two_radii.setToolTip('Winkel der Klothoide')
        self.arc_length_two_radii.setText('180')
        self.arc_length_two_radii.setPlaceholderText('Winkel')
        self.arc_length_two_radii.setFixedWidth(120)
        self.arc_length_two_radii.setValidator(QtGui.QDoubleValidator())
        self.arc_length_two_radii.textChanged.connect(self.update_two_radii_clothoid)

        self.direction_two_radii = QComboBox(self)
        self.direction_two_radii.addItems(('Rechts', 'Links'))
        self.direction_two_radii.setFixedWidth(120)
        self.direction_two_radii.activated[str].connect(self.update_two_radii_clothoid)

        form_two_radii = QFormLayout()
        form_two_radii.addRow(QLabel('Anfagsradius:'), self.first_radius)
        form_two_radii.addRow(QLabel('Endradius:'), self.second_radius)
        form_two_radii.addRow(QLabel('Winkel:'), self.arc_length_two_radii)
        form_two_radii.addRow(QLabel('Richtung:'), self.direction_two_radii)
        form_two_radii.setVerticalSpacing(0)

        # Label for warnings
        self.warning_label = QLabel(self)
        self.warning_label.setFixedWidth(600)
        self.warning_label.setStyleSheet('color: red')
        self.warning_label.move(300,0)

        # Label for coordinates
        self.end_label = QLabel(f'End Koordinate: x: {self.dict["end"][0]/self.factor}, y: {self.dict["end"][1]/self.factor}', self)
        self.end_label.move(0, 180)
        self.end_label.setFixedWidth(260)
        
        # Box with tabs
        self.tabs = QTabWidget(self)
        self.tabs.resize(260, 180)
        # Calls the function tab_handler() when a tab is clicked
        self.tabs.currentChanged.connect(self.tab_handler)

        self.tab_a = QWidget()
        self.tab_end_radius = QWidget()
        self.tab_two_radii = QWidget()

        self.tabs.addTab(self.tab_end_radius, 'Ein Radius')
        self.tabs.addTab(self.tab_two_radii, 'Zwei Radien')
        self.tabs.addTab(self.tab_a, 'A')

        self.tab_a.setLayout(form_a)
        self.tab_end_radius.setLayout(form_end_radius)
        self.tab_two_radii.setLayout(form_two_radii)

        finish_button = QPushButton('Fertig',self)
        finish_button.clicked.connect(self.finish_button_clicked)
        finish_button.move(0, 210)
        finish_button.setFixedWidth(260)

        self.update_a_clothoid()

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
    
    def finish_button_clicked(self):
        """
        Close the window and insert clothoid in to the road list
        """
        self.hide() 
        if self.arc_length_a.text() and self.a.text():
            self.parent_window.append_road_element(get_clothoid_dict(self.road[-1]['end'], self.road[-1]['endDirection'], self.dict['a'], self.dict['angle'], self.dict['angle_offset'], self.dict['type'], self.dict['end'], self.dict['localDirection']))
            del self

    def tab_handler(self):
        """
        Load the clothoid of the selected tab
        """
        tab = self.tabs.currentWidget()
        if tab == self.tab_a:
            self.update_a_clothoid()
        elif tab == self.tab_end_radius:
            self.update_end_radius_clothoid()
        elif tab == self.tab_two_radii:
            self.update_two_radii_clothoid()

    def update_a_clothoid(self):
        """
        Update the clothoid with the "a" parameters
        """
        if self.arc_length_a.text() and self.a.text():
            # Dictionary for the cothoid
            dict ={}
            dict['a'] = int(self.a.text())
            dict['angle_offset'] = 0
            dict['type'] = 'opend' if self.type_a.currentText() == 'Öffnend' else 'closing'
            dict['localDirection'] = 'right' if self.direction_a.currentText() == 'Rechts' else 'left'
            direction = 1 if dict['localDirection'] == 'right' else -1
            angle = float(self.arc_length_a.text())
            if self.check_angle(angle):
                return
            dict['angle'] = angle * direction * -1
            dict['points'] = get_clothoid(dict['a'], angle, dict['angle_offset'], direction, dict['type'])
            dict['end'] = dict['points'][-1]
            
            self.dict = dict
            self.end_label.setText(f'End Koordinate: x: {self.dict["end"][0]/self.factor}, y: {self.dict["end"][1]/self.factor}')

    def update_end_radius_clothoid(self):
        """
        Update the clothoid with the "end radius" parameters
        """
        if self.arc_length_end_radius.text() and self.end_radius.text():
            # Dictionary for the cothoid
            dict ={}
            dict['angle_offset'] = 0
            dict['type'] = 'opend' if self.type_end_radius.currentText() == 'Öffnend' else 'closing'
            dict['localDirection'] = 'right' if self.direction_end_radius.currentText() == 'Rechts' else 'left'
            direction = 1 if dict['localDirection'] == 'right' else -1
            angle = float(self.arc_length_end_radius.text())
            if self.check_angle(angle):
                return
            dict['angle'] = angle * direction * -1
            radian = math.radians(float(self.arc_length_end_radius.text()))
            end_radius = float(self.end_radius.text())
            dict['a'] = math.sqrt(end_radius**2 * 2*radian)
            radian = radian * direction
            dict['points'] = get_clothoid(dict['a'], angle, dict['angle_offset'], direction, dict['type'])
            dict['end'] = dict['points'][-1]
            
            self.dict = dict
            self.end_label.setText(f'End Koordinate: x: {self.dict["end"][0]/self.factor}, y: {self.dict["end"][1]/self.factor}')

    def update_two_radii_clothoid(self):
        """
        Update the clothoid with the "two radii" parameters
        """
        if self.arc_length_two_radii.text() and self.second_radius.text() and self.first_radius:
            start_radius = float(self.first_radius.text())
            end_radius = float(self.second_radius.text())
            if end_radius/start_radius >= 0.8 and end_radius/start_radius <= 1.2:
                # This proportion would cause bugs
                self.warning_label.setText('Das Verhälnis Endradius/Anfangsradius muss kleiner 0.9 oder größer 1.2 sein')
                return
            self.warning_label.setText('')
            # Dictionary for the cothoid
            dict ={}
            dict['localDirection'] = 'right' if self.direction_two_radii.currentText() == 'Rechts' else 'left'
            direction = 1 if dict['localDirection'] == 'right' else -1
            angle = float(self.arc_length_two_radii.text())
            if self.check_angle(angle):
                return
            dict['angle'] = angle * direction * -1
            radian = math.radians(float(self.arc_length_two_radii.text()))
            dict['type'] = 'closing'
            if start_radius < end_radius:
                dict['type'] = 'opend'
                start_radius, end_radius = end_radius, start_radius
            radian_end = radian/(1-end_radius**2/start_radius**2)
            dict['angle_offset'] = math.degrees(radian_end - radian)
            dict['a'] = end_radius * math.sqrt(2*radian_end)
            dict['points'] = get_clothoid(dict['a'], angle, dict['angle_offset'], direction, dict['type'])
            dict['end'] = dict['points'][-1]
            
            self.dict = dict
            self.end_label.setText(f'End Koordinate: x: {self.dict["end"][0]/self.factor}, y: {self.dict["end"][1]/self.factor}')
    
    def check_angle(self, angle):
        """
        Return True if the angle is between 0 and 360 
        """
        if angle <= 0 or angle > 360:
            self.warning_label.setText('Der Winkel muss zwischen 0° und 360° sein')
            return True
        else:
            self.warning_label.setText('')
            return False

def get_clothoid(a, angle, angle_offset, direction, type):
    """
    Return a list with coordinats of the clothoid for the given parameters
    """
    points = []
    arc_length_start = a*math.sqrt(2*math.radians(angle_offset))
    arc_length_end = a*math.sqrt(2*math.radians(angle_offset + angle))
    # Distance between the points
    distance = 0.04
    # l is the length of the clothoid path
    l = [i*distance for i in range(get_int(arc_length_start/distance), get_int(arc_length_end/distance)+1)]
    for i in l:
        points.append(get_clothoid_point(a, i, direction))
    move = [points[0][0]*-1, points[0][1]*-1]
    for i, point in enumerate(points):
        points[i] = rotate_point(move_point(point, move), math.radians(angle_offset)*direction)
    if type == 'opend':
        # tansform the clothoid to a opend clothoid
        points = get_inverted_points(points, math.radians(angle)*direction)
    return points

def get_inverted_points(points, radian):
    """
    Transform the given clothoid from closed to opend
    """
    new_points = []
    end = points[-1]
    for point in points:
        d = [(point[0]*-1+end[0]), (point[1]*-1+end[1])]
        new_points.append([get_int(d[0]*math.cos(radian)+d[1]*math.sin(radian)), get_int(d[0]*math.sin(radian)-d[1]*math.cos(radian))])
    return new_points[::-1]

def get_clothoid_point(a, l, direction):
    """
    Calculate a clothoid point for the given parameters
    """
    toggle = 1
    x = 0
    y = 0 
    for loops in range(20):
        x_ = toggle*l**(1+4*loops)/(a**(4*loops)*math.factorial(2*loops)*(1+4*loops)*2**(2*loops))
        y_ = toggle*l**(3+4*loops)/(a**(2+4*loops)*math.factorial(1+2*loops)*(3+4*loops)*2**(1+2*loops))
        x += x_
        y += y_
        toggle *= -1
    return [get_int(x*100) ,get_int(y*direction*100)]


class PaintClothoid(QWidget):
    def __init__(self, dict, move_window, factor, parent_window):
        super().__init__()
        self.dict = dict
        self.move_window = move_window
        self.factor = factor
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
        road_width = 75
        start = self.parent_window.start

        painter = QPainter(self)     
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.gray, road_width, cap=Qt.FlatCap))

        path = QPainterPath()
        polygon = []

        p = [QPoint(i[0]+start[0],i[1]+start[1]) for i in self.parent_window.dict['points']]
        polygon = QPolygonF(p)
        path.addPolygon(polygon)
        painter.drawPath(path)
        self.update()