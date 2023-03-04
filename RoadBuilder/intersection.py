from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit, QComboBox
from PyQt5.QtGui import QFont

from get_road_element_dict import get_intersection_dict

class IntersectionWindow(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        font = QFont('Roboto', 10)
        self.setFont(font)
        
        self.setWindowTitle('Kreuzung einfügen')
        self.resize(250, 120)
        
        self.length = QLineEdit(self)
        self.length.setToolTip('Länge der beiden Kreuzungsarme')
        self.length.setPlaceholderText('Länge')
        self.length.setValidator(QtGui.QDoubleValidator())
        self.length.resize(250,30)
        
        self.direction = QComboBox(self)
        self.direction.addItems(('Rechtskurve', 'Linkskurve', 'Gerade'))
        self.direction.resize(250, 30)
        self.direction.move(0, 40)
        
        self.finish_button = QPushButton('Fertig',self)
        self.finish_button.clicked.connect(self.finish_button_clicked)
        self.finish_button.move(0, 80)
        self.finish_button.setFixedWidth(250)
        
        self.parent_window=parent_window

        self.road = parent_window.road
        self.factor = parent_window.factor

    def finish_button_clicked(self):
        if self.length.text():
            if float(self.length.text()) > 0:
                self.hide()
                self.parent_window.append_road_element(get_intersection_dict(self.road[-1]['end'], self.road[-1]['endDirection'], self.direction.currentText(), float(self.length.text()), self.parent_window.open_intersections, self.factor))
                self.parent_window.update()
                del self
        