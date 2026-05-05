"""Initiate the application instance and load main window"""

import sys

from PyQt6.QtWidgets import QApplication

from dash.gui.mainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
