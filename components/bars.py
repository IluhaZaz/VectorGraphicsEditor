from PyQt5.QtWidgets import QToolBar, QPushButton, QSlider, QMainWindow
from PyQt5.QtCore import Qt

from components.svg_utils import ColorTextEdit


class ToolBar(QToolBar):

    def __init__(self, title, parent):
        super().__init__(title, parent)

        self.editor: QMainWindow = parent

        save = QPushButton("Save", self)
        save.clicked.connect(self.on_save)
        self.addWidget(save)

        close = QPushButton("Close", self)
        close.clicked.connect(self.on_close)
        self.addWidget(close)

        self.stroke_color = QPushButton("Stroke color", self)
        self.stroke_color.clicked.connect(self.change_stroke_color)
        self.addWidget(self.stroke_color)

        self.fill_color = QPushButton("Fill color", self)
        self.fill_color.clicked.connect(self.change_fill_color)
        self.addWidget(self.fill_color)

        self.color_field = ColorTextEdit(self)
        self.color_field.setFixedSize(90, 30)
        self.addWidget(self.color_field)

        self.opacity = QSlider(Qt.Orientation.Horizontal, self)
        self.opacity.setMinimum(0)
        self.opacity.setMaximum(100)
        self.opacity.setValue(100)
        self.opacity.setFixedWidth(100)
        self.addWidget(self.opacity)

    def on_save(self):
        pass

    def on_close(self):
        self.parent().close()

    def change_stroke_color(self):
        opacity = self.opacity.value()/100
        color = self.color_field.toPlainText()
        self.stroke_color.setStyleSheet(f"background: {color}; opacity: {opacity};")
        self.editor.drawer.stroke_color = color
        self.editor.drawer.stroke_opacity = opacity

    def change_fill_color(self):
        opacity = self.opacity.value()/100
        color = self.color_field.toPlainText()
        self.fill_color.setStyleSheet(f"background: {color}; opacity: {opacity};")
        self.editor.drawer.fill = color
        self.editor.drawer.fill_opacity = opacity


class FiguresBar(QToolBar):

    def __init__(self, title, parent):
        super().__init__(title, parent)

        self.editor: QMainWindow = parent

        add_rect = QPushButton("Add rectangle", self)
        add_rect.clicked.connect(self.add_rect)
        self.addWidget(add_rect)

        add_circle = QPushButton("Add circle", self)
        add_circle.clicked.connect(self.add_circle)
        self.addWidget(add_circle)

        add_line = QPushButton("Add line", self)
        add_line.clicked.connect(self.add_line)
        self.addWidget(add_line)

        delete_figure = QPushButton("Delete figure", self)
        delete_figure.clicked.connect(self.delete_figure)
        self.addWidget(delete_figure)

    def add_rect(self):
        self.editor.drawer.figure = "rect"

    def add_circle(self):
        self.editor.drawer.figure = "circle"

    def add_line(self):
        self.editor.drawer.figure = "line"

    def delete_figure(self):
        self.editor.canvas.delete_figure(self.editor.drawer.selected)