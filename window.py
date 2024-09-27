import sys

import svgwrite

from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QGridLayout, QToolBar, QAction
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QColor


class ToolBar(QToolBar):

    def __init__(self, title, parent):
        super().__init__(title, parent)

        action_save = QAction("Save", self)
        action_save.triggered.connect(self.on_save)

        action_close = QAction("Close", self)
        action_close.triggered.connect(self.on_close)

        self.addActions((action_save, action_close))
    

    def on_save(self):
        pass

    def on_close(self):
        window.close()


class FiguresBar(QToolBar):

    def __init__(self, title, parent):
        super().__init__(title, parent)

        action_add_rect = QAction("Add rectangle", self)
        action_add_rect.triggered.connect(self.add_rect)

        action_add_circle = QAction("Add rectangle", self)
        action_add_circle.triggered.connect(self.add_circle)

        action_add_line = QAction("Add line", self)
        action_add_line.triggered.connect(self.add_line)

        self.addActions((action_add_rect, action_add_circle, action_add_line))

    def add_rect(self):
        pass

    def add_circle(self):
        pass

    def add_line(self):
        pass


class Ui_MainWindow:
    
    def setup_ui(self, main_window: QMainWindow):
        main_window.setWindowTitle("VectorGraphicsEditor")

        main_window.resize(QApplication.primaryScreen().size())

        main_window.central_widget = QWidget()
        main_window.setCentralWidget(main_window.central_widget)

        main_window.tool_bar = ToolBar("Tool bar", parent=main_window)
        main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, main_window.tool_bar)

        main_window.figures_bar = FiguresBar("Tool bar", parent=main_window)
        main_window.addToolBar(Qt.ToolBarArea.RightToolBarArea, main_window.figures_bar)

        main_window.canvas = QSvgWidget(main_window)
        main_window.canvas.setStyleSheet("border:5px solid black;")
        main_window.canvas.setGeometry(70, 100, main_window.size().width() - 200, main_window.size().height() - 300)
        main_window.dwg = svgwrite.Drawing()


class VectorGraphicsEditor(QMainWindow):

    def __init__(self) -> None:
        super().__init__()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VectorGraphicsEditor()
    ui_setuper = Ui_MainWindow()

    ui_setuper.setup_ui(window) 
    window.show()
    sys.exit(app.exec_())