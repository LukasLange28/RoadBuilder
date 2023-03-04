import sys

from PyQt5.QtWidgets import QApplication

from build_road_gui import MainWindow

def start():
    App = QApplication(sys.argv)
    MainWindow()
    sys.exit(App.exec())

if __name__ == '__main__':
    start()