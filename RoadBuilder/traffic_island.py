from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QGroupBox
from PyQt5.QtGui import QFont

from RoadBuilder.get_road_element_dict import get_traffic_island_dict

class TrafficIslandWindow(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        font = QFont('Roboto', 10)
        self.setFont(font)

        self.setWindowTitle('Fußgängerinsel einfügen')
        self.resize(300, 160)
        
        self.island_width = QLineEdit()
        self.island_width.setMinimumWidth(100)
        self.island_width.setValidator(QtGui.QDoubleValidator())
        
        self.zebra_length = QLineEdit()
        self.zebra_length.setMinimumWidth(100)
        self.zebra_length.setValidator(QtGui.QDoubleValidator())
        
        self.curve_area_length = QLineEdit()
        self.curve_area_length.setMinimumWidth(100)
        self.curve_area_length.setValidator(QtGui.QDoubleValidator())
        
        self.curvature = QLineEdit()
        self.curvature.setMinimumWidth(100)
        self.curvature.setValidator(QtGui.QDoubleValidator())
        self.curvature.setToolTip('0 bis 1')
        
        self.finish_button = QPushButton('Fertig',self)
        self.finish_button.clicked.connect(self.finish_button_clicked)
        self.finish_button.setFixedWidth(150)
        
        form = QFormLayout()
        form.addRow(QLabel('Inselbreite:'), self.island_width)
        form.addRow(QLabel('Zebrastreifenlänge:'), self.zebra_length)
        form.addRow(QLabel('Kurvenbereichslänge:'), self.curve_area_length)
        form.addRow(QLabel('Krümmung:'), self.curvature)
        form.addRow(self.finish_button)
        form.setVerticalSpacing(1)
        form.setAlignment(self.finish_button, QtCore.Qt.AlignCenter)

        self.form_group_box = QGroupBox(self)
        self.form_group_box.setLayout(form)
        self.form_group_box.setMinimumSize(300,180)
        self.form_group_box.move(0, -20)
        
        self.parent_window = parent_window
        self.road = parent_window.road
        self.factor = parent_window.factor
    
    def finish_button_clicked(self):
        
        if self.island_width.text() and self.zebra_length.text() and self.curve_area_length.text() and self.curvature.text():
            island_width = float(self.island_width.text())
            zebra_length = float(self.zebra_length.text())
            curve_area_length = float(self.curve_area_length.text())
            curvature = float(self.curvature.text())
            
            if island_width > 0 and zebra_length > 0 and curve_area_length > 0 and curvature >= 0 and curvature <= 1:
                self.hide()
                self.parent_window.append_road_element(get_traffic_island_dict(self.road[-1]['end'], self.road[-1]['endDirection'], zebra_length, island_width, curve_area_length, curvature, self.factor))
                self.parent_window.update()
                del self