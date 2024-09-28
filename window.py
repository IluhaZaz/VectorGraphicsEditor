import sys

import svgwrite

from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QToolBar, QAction
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QMouseEvent
import svgwrite.shapes


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

        action_add_circle = QAction("Add circle", self)
        action_add_circle.triggered.connect(self.add_circle)

        action_add_line = QAction("Add line", self)
        action_add_line.triggered.connect(self.add_line)

        self.addActions((action_add_rect, action_add_circle, action_add_line))

    def add_rect(self):
        self.parent().drawer.figure = "rect"

    def add_circle(self):
        self.parent().drawer.figure = "circle"

    def add_line(self):
        self.parent().drawer.figure = "line"


class Canvas(QSvgWidget):

    def __init__(self, parent):
        super().__init__(parent)
        

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            draw: Drawer = self.parent().drawer

            start = draw.start
            end = event.pos().x(), event.pos().y()

            match draw.figure:
                case "circle":
                    r = (((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5)//2
                    center = (start[0] + end[0])//2, (start[1] + end[1])//2
                    draw.dwg.add(svgwrite.shapes.Circle(center=center, 
                                                        r=r, 
                                                        stroke=draw.stroke_color, 
                                                        stroke_width=draw.width, 
                                                        fill = draw.fill))
                case "rect":
                    size = (abs(start[0] - end[0]), abs(start[1] - end[1]))
                    if start[0] > end[0]:
                        if start[1] > end[1]:
                            top_left = end
                        else:
                            top_left = end[0], start[1]
                    else:
                        if start[1] > end[1]:
                            top_left = start[0], end[1]
                        else:
                            top_left = start
                    draw.dwg.add(svgwrite.shapes.Rect(insert=top_left,
                                                      size=size))
                case "line":
                    draw.dwg.add(svgwrite.shapes.Line(start=start,
                                                      end=end,
                                                      stroke=draw.stroke_color,
                                                      stroke_width=draw.width))
                    
            self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
         self.parent().drawer.start = (event.pos().x(), event.pos().y())


class VectorGraphicsEditor(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.canvas: Canvas
        self.central_widget: QWidget
        self.tool_bar: ToolBar
        self.figures_bar: FiguresBar
        self.drawer: Drawer


class Drawer:

    def __init__(self, parent: VectorGraphicsEditor) -> None:
        size = parent.canvas.size().width(), parent.canvas.size().height()
        self.dwg = svgwrite.Drawing(profile="full", size=size)
        self.figure = None
        self.stroke_color = "black"
        self.fill = "black"
        self.width = 3
        self.start = None


class Ui_MainWindow:
    
    def setup_ui(self, main_window: VectorGraphicsEditor):
        main_window.setWindowTitle("VectorGraphicsEditor")

        main_window.resize(QApplication.primaryScreen().size())

        main_window.central_widget = QWidget()
        main_window.setCentralWidget(main_window.central_widget)

        main_window.tool_bar = ToolBar("Tool bar", parent=main_window)
        main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, main_window.tool_bar)

        main_window.figures_bar = FiguresBar("Tool bar", parent=main_window)
        main_window.addToolBar(Qt.ToolBarArea.RightToolBarArea, main_window.figures_bar)

        main_window.canvas = Canvas(main_window)
        main_window.canvas.setStyleSheet("border:5px solid black;")
        main_window.canvas.setGeometry(70, 100, main_window.size().width() - 200, main_window.size().height() - 300)
        
        main_window.drawer = Drawer(main_window)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VectorGraphicsEditor()
    ui_setuper = Ui_MainWindow()

    ui_setuper.setup_ui(window) 
    window.show()
    sys.exit(app.exec_())