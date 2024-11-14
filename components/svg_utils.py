import svgwrite

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QPoint, QByteArray
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
        self.figure = None
        self.stroke = constants["def_stroke"]
        self.fill = constants["def_fill"]
        self.width = constants["def_stroke_width"]
        self.stroke_opacity = constants["def_stroke_opacity"]
        self.fill_opacity = constants["def_fill_opacity"]

        self.start = None
        self.prev_pos: QPoint = None

        self.selected: SvgShape = None
        self.layer: Layer = parent.canvas.layers[0]

        self.selector_side: str = None
        self.selector_point_indx: int = None


class QToggleButton(QPushButton):

    def __init__(self, text, parent):
        super().__init__(text, parent)

        self.setCheckable(True)
        self.setChecked(False)


class Layer(QPushButton):
    def __init__(self, parent, name: str):
        super().__init__(parent=parent, text=name)
        self.name = name
        self.figures: list[SvgShape] = []
        self.g = svgwrite.container.Group(id=name)

        self.setStyleSheet("background: rgba(240,128,128, 0.8);")
    
    def mousePressEvent(self, e):
        canvas = self.parent().editor.canvas
        draw: Drawer = self.parent().editor.drawer

        if draw.selected is not None:
            canvas.dwg.elements.remove(draw.selected.params["selector"])
            draw.selected = None

        self.parent().editor.drawer.layer = self
        canvas.load(QByteArray(canvas.dwg.tostring().encode('utf-8')))
        svg =  canvas._make_svg_from_element(draw.layer.g).encode('utf-8')
        self.parent().preview.load(QByteArray(svg))

        self.setStyleSheet("background: rgba(240,128,128, 1);")
        for layer in canvas.layers:
            if layer != self:
                layer.setStyleSheet("background: rgba(240,128,128, 0.8);")

        return super().mousePressEvent(e)
