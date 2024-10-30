import svgwrite

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QPoint
from json import load


with open('constants.json', 'r') as f:
    constants = load(f)

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
        self.stroke = constants["def_stroke"]
        self.fill = constants["def_fill"]
        self.width = constants["def_stroke_width"]
        self.stroke_opacity = constants["def_stroke_opacity"]
        self.fill_opacity = constants["def_fill_opacity"]
        self.start = None
        self.selected: SvgShape = None
        self.prev_pos: QPoint = None


class QToggleButton(QPushButton):

    def __init__(self, text, parent):
        super().__init__(text, parent)

        self.setCheckable(True)
        self.setChecked(False)
