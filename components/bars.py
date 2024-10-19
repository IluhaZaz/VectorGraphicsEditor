import xml.etree.ElementTree as ET
import svgwrite
import svgwrite.container

from PyQt5.QtWidgets import QToolBar, QPushButton, QSlider, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QByteArray

from components.svg_utils import ColorTextEdit, SvgShape, Drawer


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

        self.color_field = ColorTextEdit(self)
        self.color_field.setFixedSize(90, 30)
        self.addWidget(self.color_field)

        self.opacity = QSlider(Qt.Orientation.Horizontal, self)
        self.opacity.setMinimum(0)
        self.opacity.setMaximum(100)
        self.opacity.setValue(100)
        self.opacity.setFixedWidth(100)
        self.addWidget(self.opacity)

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
            self.editor.canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))
        
        draw.dwg.save()

    def on_close(self):
        self.editor.close()

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