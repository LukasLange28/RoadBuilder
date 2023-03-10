from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox, QDialog
from PyQt5.QtGui import QFont

class SelectLineStyleWindow(QDialog):
    
    def __init__(self):
        super().__init__()
        
        font = QFont('Roboto', 10)
        self.setFont(font)

        self.resize(260, 210)
        self.setWindowTitle('Linien Konfigurator')

        self.line_styles = ('Durchgehende Linie', 'Gestrichelte Linie', 'Keine Linie',
            # The following line styles are described in the doku but not implemented
            #'Doppelte Linie', 'Doppelte gestrichelte Linie', 'Durchgehende/Gestrichelte Linie', 'Gestrichelte/Durchgehende Linie'
            )
        
        self.left_line_label = QLabel(self)
        self.left_line_label.setText('Linke Linie:')
        self.left_line_label.move(0, 0)

        self.left_line = QComboBox(self)
        self.left_line.addItems(self.line_styles)
        self.left_line.move(0,30)
        
        self.middle_line_label = QLabel(self)
        self.middle_line_label.setText('Mittlere Linie:')
        self.middle_line_label.move(0, 60)

        self.middle_line = QComboBox(self)
        self.middle_line.addItems(self.line_styles)
        self.middle_line.setCurrentText('Gestrichelte Linie')
        self.middle_line.move(0, 90)

        self.right_line_label = QLabel(self)
        self.right_line_label.setText('Rechte Linie:')
        self.right_line_label.move(0, 120)

        self.rigth_line = QComboBox(self)
        self.rigth_line.addItems(self.line_styles)
        self.rigth_line.move(0, 150)

        self.finish_button = QPushButton('Fertig',self)
        self.finish_button.clicked.connect(self.finish_button_clicked)
        self.finish_button.move(0, 180)
        self.finish_button.setFixedWidth(200)
    
    def finish_button_clicked(self):
        self.close()
    
    def get_value(self):
        
        return {'rightLine': self.get_name(self.rigth_line.currentText()), 'middleLine': self.get_name(self.middle_line.currentText()), 'leftLine': self.get_name(self.left_line.currentText())}
    
    def get_name(self, name):
        true_names = ['solid', 'dashed', 'missing', 
            # The following line styles are described in the doku but not implemented
            #'double_solid', 'double_dashed', 'dashed_solid', 'solid_dashed'
            ]
        return true_names[list(self.line_styles).index(name)]
