import svgwrite

from PyQt5.QtWidgets import QTextEdit, QPushButton


class SvgShape:
    def __init__(self, shape: str, obj, **params) -> None:
        self.shape: str = shape
        self.obj = obj
        self.params = params


class Drawer:

    def __init__(self, parent) -> None:
        self.size = parent.canvas.size().width(), parent.canvas.size().height()
        self.dwg = svgwrite.Drawing(profile="full", size=self.size)
        self.figure = None
        self.stroke_color = "black"
        self.fill = "white"
        self.width = 3
        self.stroke_opacity = 1
        self.fill_opacity = 0
        self.start = None
        self.selected: SvgShape = None


class QToggleButton(QPushButton):

    def __init__(self, text, parent):
        super().__init__(text, parent)

        self.setCheckable(True)
        self.setChecked(False)
