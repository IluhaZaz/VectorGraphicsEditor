import sys

import svgwrite

from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QToolBar, QAction
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray, Qt, QPoint
from PyQt5.QtGui import QMouseEvent
import svgwrite.shapes


class SvgShape:
    def __init__(self, shape: str, obj, **params) -> None:
        self.shape: str = shape
        self.obj = obj
        self.params = params


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
        self.figures: list[SvgShape] = []
        

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            draw: Drawer = self.parent().drawer

            start = draw.start
            end = event.pos().x(), event.pos().y()

            dist = ((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5
            if dist < 3:
                self.select_figure(event.pos())
                return

            match draw.figure:

                case "circle":
                    r = (((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5)//2
                    center = (start[0] + end[0])//2, (start[1] + end[1])//2
                    circle = svgwrite.shapes.Circle(center=center, 
                                                    r=r, 
                                                    stroke=draw.stroke_color, 
                                                    stroke_width=draw.width, 
                                                    fill = draw.fill)
                    draw.dwg.add(circle)
                    self.figures.append(SvgShape("circle", circle, center=center, r=r))

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
                    rect = svgwrite.shapes.Rect(insert=top_left,
                                                size=size,
                                                stroke=draw.stroke_color, 
                                                stroke_width=draw.width, 
                                                fill = draw.fill)
                    draw.dwg.add(rect)
                    self.figures.append(SvgShape("rect", rect, insert=top_left, size=size))

                case "line":
                    line = svgwrite.shapes.Line(start=start,
                                                end=end,
                                                stroke=draw.stroke_color,
                                                stroke_width=draw.width)
                    draw.dwg.add(line)
                    self.figures.append(SvgShape("line", line, start=start, end=end))
                    
            self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
         self.parent().drawer.start = (event.pos().x(), event.pos().y())

    def select_figure(self, pos: QPoint):
        tolerance = 3
        
        tl_select, select_size = None, None
        select_rect = None
        draw: Drawer = self.parent().drawer

        if draw.selected:
            draw.dwg.elements.remove(draw.selected.params["selector"])
            draw.selected.params.pop("selector")
            draw.selected = None

        for figure in self.figures[::-1]:
            match figure.shape:
                case'circle':
                    center = figure.params["center"]
                    r = figure.params['r']
                    if ((center[0] - pos.x()) ** 2 + (center[1] - pos.y()) ** 2) ** 0.5 <= r:
                        print(f"Circle selected: center={center}, radius={r}")

                        tl_select = center[0] - r, center[1] - r
                        select_size = (2*r, 2*r)
                        select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                                size=select_size,
                                                stroke="blue",
                                                fill="none"
                                                )
                        draw.selected = figure
                        break

                case 'rect':
                    top_left = figure.params['insert']
                    size = figure.params['size']
                    if top_left[0] <= pos.x() <= top_left[0] + size[0] and top_left[1] <= pos.y() <= top_left[1] + size[1]:
                        print(f"Rectangle selected: top_left={top_left}, size={size}")

                        tl_select = top_left[0] - 10, top_left[1] - 10
                        select_size = (size[0] + 20, size[1] + 20)
                        select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                                size=select_size,
                                                stroke="blue",
                                                fill="none"
                                                )

                        draw.selected = figure
                        break

                case 'line':
                    start = figure.params['start']
                    end = figure.params['end']

                    distance_to_line = abs((end[1] - start[1]) * pos.x() - (end[0] - start[0]) * pos.y() + end[0] * start[1] - end[1] * start[0]) / ((end[1] - start[1])**2 + (end[0] - start[0])**2) ** 0.5
                    if distance_to_line <= tolerance:
                        print(f"Line selected: start={start}, end={end}")

                        if start[0] > end[0]:
                            if start[1] > end[1]:
                                tl_select = end
                            else:
                                tl_select = end[0], start[1]
                        else:
                            if start[1] > end[1]:
                                tl_select = start[0], end[1]
                            else:
                                tl_select = start
                        select_size = (abs(start[0] - end[0]), abs(start[1] - end[1]))

                        select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                                size=select_size,
                                                stroke="blue",
                                                fill="none"
                                                )

                        draw.selected = figure
                        break

        if select_rect:
            draw.dwg.add(select_rect)
            draw.selected.params["selector"] = select_rect
            
        self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))

    def delete_figure(self, figure: SvgShape):
        draw: Drawer = self.parent().drawer
        if draw.selected is not None:
            draw.dwg.elements.remove(figure.obj)
            self.figures.remove(figure) 


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
        self.fill = "pink"
        self.width = 3
        self.start = None
        self.selected: SvgShape = None


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