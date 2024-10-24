import xml.etree.ElementTree as ET
import svgwrite
import svgwrite.container

from PyQt5.QtWidgets import QToolBar, QPushButton, QMainWindow, QFileDialog, QColorDialog, QButtonGroup
from PyQt5.QtCore import QByteArray

from components.svg_utils import SvgShape, Drawer, QToggleButton


class ToolBar(QToolBar):

    def __init__(self, title, parent):
        super().__init__(title, parent)

        self.editor: QMainWindow = parent

        open = QPushButton("Open", self)
        open.clicked.connect(self.open)
        self.addWidget(open)

        save = QPushButton("Save", self)
        save.clicked.connect(self.on_save)
        self.addWidget(save)

        save_as = QPushButton("Save as", self)
        save_as.clicked.connect(self.on_save_as)
        self.addWidget(save_as)

        close = QPushButton("Close", self)
        close.clicked.connect(self.on_close)
        self.addWidget(close)

        self.stroke_color = QPushButton("Stroke color", self)
        self.stroke_color.clicked.connect(self.change_stroke_color)
        self.addWidget(self.stroke_color)

        self.fill_color = QPushButton("Fill color", self)
        self.fill_color.clicked.connect(self.change_fill_color)
        self.addWidget(self.fill_color)

    def open(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть файл SVG", "", "SVG Files (*.svg);;All Files (*)", options=options)
        if filename:
            tree = ET.parse(filename)
            root = tree.getroot()

            dwg = svgwrite.Drawing(profile='full', size=self.editor.drawer.size)
            for shape in root:
                if shape.tag == '{http://www.w3.org/2000/svg}circle':
                    cx = int(shape.attrib['cx'])
                    cy = int(shape.attrib['cy'])
                    r = float(shape.attrib['r'])
                    fill = shape.attrib.get('fill', 'none')
                    fill_opacity = float(shape.attrib.get('fill-opacity', 1))
                    stroke = shape.attrib.get('stroke', '#FFFFFF')
                    stroke_opacity = float(shape.attrib.get('stroke-opacity', 1))
                    stroke_width = int(shape.attrib.get('stroke-width', 3))

                    circle = dwg.circle(center=(cx, cy), r=r, 
                                       fill=fill, 
                                       stroke=stroke, 
                                       fill_opacity=fill_opacity, 
                                       stroke_opacity=stroke_opacity, 
                                       stroke_width=stroke_width)

                    dwg.add(circle)
                    self.editor.canvas.figures.append(SvgShape("circle", circle, center=(cx, cy), r=r))

                elif shape.tag == '{http://www.w3.org/2000/svg}rect':
                    x = int(shape.attrib.get('x', 0))
                    y = int(shape.attrib.get('y', 0))
                    width = int(shape.attrib.get('width', 0))
                    height = int(shape.attrib.get('height', 0))
                    fill = shape.attrib.get('fill', 'none')
                    fill_opacity = float(shape.attrib.get('fill-opacity', 1))
                    stroke = shape.attrib.get('stroke', '#FFFFFF')
                    stroke_opacity = float(shape.attrib.get('stroke-opacity', 1))
                    stroke_width = int(shape.attrib.get('stroke-width', 3))

                    rect = dwg.rect(insert=(x, y), size=(width, height),
                                    fill=fill, 
                                    stroke=stroke, 
                                    fill_opacity=fill_opacity, 
                                    stroke_opacity=stroke_opacity, 
                                    stroke_width=stroke_width)
                    dwg.add(rect)
                    self.editor.canvas.figures.append(SvgShape("rect", rect, insert=(x, y), size=(width, height)))

                elif shape.tag == '{http://www.w3.org/2000/svg}line':
                    x1 = int(shape.attrib.get('x1', 0))
                    y1 = int(shape.attrib.get('y1', 0))
                    x2 = int(shape.attrib.get('x2', 0))
                    y2 = int(shape.attrib.get('y2', 0))
                    stroke = shape.attrib.get('stroke', '#FFFFFF')
                    stroke_opacity = float(shape.attrib.get('stroke-opacity', 1))
                    stroke_width = int(shape.attrib.get('stroke-width', 3))

                    line = dwg.line(start=(x1, y1), end=(x2, y2), 
                                    stroke=stroke, 
                                    stroke_opacity=stroke_opacity, 
                                    stroke_width=stroke_width
                                    )
                    dwg.add(line)
                    self.editor.canvas.figures.append(SvgShape("line", line, start=(x1, y1), end=(x2, y2)))
            self.editor.drawer.dwg = dwg

            self.editor.canvas.load(QByteArray(self.editor.drawer.dwg.tostring().encode('utf-8')))


    def on_save_as(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить файл SVG", "", "SVG Files (*.svg);;All Files (*)", options=options)
        
        if filename:
            draw: Drawer = self.editor.drawer
            if draw.selected:
                draw.dwg.elements.remove(draw.selected.params["selector"])
                draw.selected.params.pop("selector")
                draw.selected = None

            draw.dwg.filename = filename
            draw.dwg.save()

    def on_save(self):
        draw: Drawer = self.editor.drawer
        if draw.dwg.filename == "noname.svg":
            options = QFileDialog.Options()
            filename, _ = QFileDialog.getSaveFileName(self, "Сохранить файл SVG", "", "SVG Files (*.svg);;All Files (*)", options=options)
            draw.dwg.filename = filename

        if draw.selected:
            draw.dwg.elements.remove(draw.selected.params["selector"])
            draw.selected.params.pop("selector")
            draw.selected = None
            self.editor.canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))
        
        draw.dwg.save()

    def on_close(self):
        self.editor.close()

    def change_stroke_color(self):
        color = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
        opacity = color.alphaF()
        color = "rgb" + str(color.getRgb()[:-1])

        self.stroke_color.setStyleSheet(f"background: {color};")
        self.editor.drawer.stroke_color = color
        self.editor.drawer.stroke_opacity = opacity

    def change_fill_color(self):
        color = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
        opacity = color.alphaF()
        color = "rgb" + str(color.getRgb()[:-1])

        self.fill_color.setStyleSheet(f"background: {color};")
        self.editor.drawer.fill = color
        self.editor.drawer.fill_opacity = opacity


class FiguresBar(QToolBar):

    def __init__(self, title, parent):
        super().__init__(title, parent)

        self.editor: QMainWindow = parent

        self.add_rect_btn = QToggleButton("Add rectangle", self)
        self.addWidget(self.add_rect_btn)

        self.add_circle_btn = QToggleButton("Add circle", self)
        self.addWidget(self.add_circle_btn)

        self.add_line_btn = QToggleButton("Add line", self)
        self.addWidget(self.add_line_btn)

        delete_figure = QPushButton("Delete figure", self)
        delete_figure.clicked.connect(self.delete_figure)
        self.addWidget(delete_figure)

        self.add_rect_btn.clicked.connect(self.add_rect)
        self.add_circle_btn.clicked.connect(self.add_circle)
        self.add_line_btn.clicked.connect(self.add_line)

        self.buttons: list[QToggleButton] = [self.add_rect_btn, self.add_circle_btn, self.add_line_btn]

    def add_rect(self):
        if self.add_rect_btn.isChecked():
            self.add_rect_btn.setChecked(True)
            self.editor.drawer.figure = "rect"
        else:
            self.add_rect_btn.setChecked(False)
            self.editor.drawer.figure = None
        for button in self.buttons:
            if button != self.add_rect_btn:
                button.setChecked(False)

    def add_circle(self):
        if self.add_circle_btn.isChecked():
            self.add_circle_btn.setChecked(True)
            self.editor.drawer.figure = "circle"
        else:
            self.add_circle_btn.setChecked(False)
            self.editor.drawer.figure = None
        for button in self.buttons:
            if button != self.add_circle_btn:
                button.setChecked(False)

    def add_line(self):
        if self.add_line_btn.isChecked():
            self.add_line_btn.setChecked(True)
            self.editor.drawer.figure = "line"
        else:
            self.add_line_btn.setChecked(False)
            self.editor.drawer.figure = None
        for button in self.buttons:
            if button != self.add_line_btn:
                button.setChecked(False)

    def delete_figure(self):
        self.editor.canvas.delete_figure(self.editor.drawer.selected)
