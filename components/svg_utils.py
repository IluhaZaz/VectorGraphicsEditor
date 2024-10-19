import svgwrite

from PyQt5.QtWidgets import QTextEdit


class SvgShape:
    def __init__(self, shape: str, obj, **params) -> None:
        self.shape: str = shape
        self.obj = obj
        self.params = params


class ColorTextEdit(QTextEdit):
    def __init__(self, parent):
        super().__init__("#", parent)
        self.limit = 7

    def keyPressEvent(self, event):
        if len(self.toPlainText()) < self.limit or event.key() in (16777219, 16777223):
            super().keyPressEvent(event)


class Drawer:

    def __init__(self, parent) -> None:
        size = parent.canvas.size().width(), parent.canvas.size().height()
        self.dwg = svgwrite.Drawing(profile="full", size=size)
        self.figure = None
        self.stroke_color = "black"
        self.fill = "white"
        self.width = 3
        self.stroke_opacity = 1
        self.fill_opacity = 0
        self.start = None
        self.selected: SvgShape = None