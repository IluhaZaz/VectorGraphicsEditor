import xml.etree.ElementTree as ET
import svgwrite

from PyQt5.QtWidgets import (QToolBar, 
                             QPushButton, 
                             QMainWindow, 
                             QFileDialog, 
                             QColorDialog, 
                             QSpinBox, 
                             QLabel, 
                             QInputDialog)
from PyQt5.QtGui import QColor
from PyQt5.QtSvg import QSvgWidget
from json import load

from components.svg_utils import SvgShape, Drawer, QToggleButton, Layer


with open('constants.json', 'r') as f:
    constants = load(f)

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

        self.font_size_lbl = QLabel(parent=self, text="Font size")
        self.font_size_lbl.setStyleSheet("QLabel{background-color: rgba(240,128,128, 0.8); padding: 0 10px;};")
        self.addWidget(self.font_size_lbl)

        self.font_size = QSpinBox(parent=self)
        self.font_size.setMinimum(3)
        self.font_size.setMaximum(1000)
        self.font_size.setValue(constants["def_font_size"])
        self.font_size.valueChanged.connect(self.change_font_size)
        self.font_size.setFixedSize(100, 30)
        self.addWidget(self.font_size)

        self.stroke_w_lbl = QLabel(parent=self, text="Stroke width")
        self.stroke_w_lbl.setStyleSheet("QLabel{background-color: rgba(240,128,128, 0.8); padding: 0 10px;};")
        self.addWidget(self.stroke_w_lbl)

        self.stroke_w = QSpinBox(parent=self)
        self.stroke_w.setMinimum(0)
        self.stroke_w.setMaximum(1000)
        self.stroke_w.setValue(constants["def_stroke_width"])
        self.stroke_w.valueChanged.connect(self.change_stroke_width)
        self.stroke_w.setFixedSize(100, 30)
        self.addWidget(self.stroke_w)

        foreground = QPushButton("To foreground", self)
        foreground.clicked.connect(self.to_foreground)
        self.addWidget(foreground)

        background = QPushButton("To background", self)
        background.clicked.connect(self.to_background)
        self.addWidget(background)

    def open(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть файл SVG", "", "SVG Files (*.svg);;All Files (*)", options=options)
        if filename:
            tree = ET.parse(filename)
            root = tree.getroot()

            dwg = svgwrite.Drawing(profile='full', size=self.editor.drawer.size, filename=filename)

            self.editor.canvas.dwg = dwg
            self.editor.canvas.layers = []

            elements = []
            layer_bar = self.parent().layer_bar
            layer_bar.clear()

            layer_bar.preview = QSvgWidget(layer_bar)
            layer_bar.preview.setFixedSize(constants["preview_w"], constants["preview_h"])
            layer_bar.addWidget(layer_bar.preview)
            layer_bar.preview.setStyleSheet("background: white; border:5px solid rgba(240,128,128, 0.8);")

            layer_bar.add_layer_bnt = QPushButton(parent=layer_bar, text="Add layer")
            layer_bar.add_layer_bnt.clicked.connect(layer_bar.add_layer)
            layer_bar.addWidget(layer_bar.add_layer_bnt)

            new_size = int(root.attrib["width"]), int(root.attrib["height"])
            self.editor.canvas.setFixedSize(*new_size)
            self.editor.canvas.dwg.attribs = {'width': new_size[0], 'height': new_size[1]}

            preview_size = new_size[0]//7, new_size[1]//7
            self.editor.layer_bar.preview.setFixedSize(*preview_size)

            num = 0
            for shape in root:
                if shape.tag == '{http://www.w3.org/2000/svg}g':
                    name = shape.attrib["id"]
                    self.parent().layer_bar._add_layer(name)

                    namespace = {'svg': 'http://www.w3.org/2000/svg'}
                    group = shape.findall(".//svg:*", namespaces=namespace)
                    if group:
                        elements.append((num, group))
                    num += 1
                    
            for indx, layer in elements:
                 for shape in layer:

                    fill = shape.attrib.get('fill', constants["def_fill"])
                    fill_opacity = float(shape.attrib.get('fill-opacity', constants["def_fill_opacity"]))
                    stroke = shape.attrib.get('stroke', constants["def_stroke"])
                    stroke_opacity = float(shape.attrib.get('stroke-opacity', constants["def_stroke_opacity"]))
                    stroke_width = int(shape.attrib.get('stroke-width', constants["def_stroke_width"]))

                    match(shape.tag):
                        case '{http://www.w3.org/2000/svg}circle':
                            cx = int(shape.attrib['cx'])
                            cy = int(shape.attrib['cy'])
                            r = float(shape.attrib['r'])

                            circle = dwg.circle(center=(cx, cy), r=r, 
                                            fill=fill, 
                                            stroke=stroke, 
                                            fill_opacity=fill_opacity, 
                                            stroke_opacity=stroke_opacity, 
                                            stroke_width=stroke_width)

                            self.editor.canvas.layers[indx].figures.append(SvgShape("circle", 
                                                                                    circle, 
                                                                                    center=(cx, cy), 
                                                                                    r=r)
                                                                                    )
                            self.editor.canvas.layers[indx].g.add(circle)

                        case '{http://www.w3.org/2000/svg}rect':
                            x = int(shape.attrib.get('x', 0))
                            y = int(shape.attrib.get('y', 0))
                            width = int(shape.attrib.get('width', 0))
                            height = int(shape.attrib.get('height', 0))

                            rect = dwg.rect(insert=(x, y), size=(width, height),
                                            fill=fill, 
                                            stroke=stroke, 
                                            fill_opacity=fill_opacity, 
                                            stroke_opacity=stroke_opacity, 
                                            stroke_width=stroke_width)
                            
                            self.editor.canvas.layers[indx].figures.append(SvgShape("rect", 
                                                                                    rect, 
                                                                                    insert=(x, y), 
                                                                                    size=(width, height))
                                                                                    )
                            self.editor.canvas.layers[indx].g.add(rect)

                        case '{http://www.w3.org/2000/svg}line':
                            x1 = int(shape.attrib.get('x1', 0))
                            y1 = int(shape.attrib.get('y1', 0))
                            x2 = int(shape.attrib.get('x2', 0))
                            y2 = int(shape.attrib.get('y2', 0))

                            line = dwg.line(start=(x1, y1), end=(x2, y2), 
                                            stroke=stroke, 
                                            stroke_opacity=stroke_opacity, 
                                            stroke_width=stroke_width
                                            )
                            self.editor.canvas.layers[indx].figures.append(SvgShape("line", 
                                                                                    line, 
                                                                                    start=(x1, y1), 
                                                                                    end=(x2, y2))
                                                                                    )
                            self.editor.canvas.layers[indx].g.add(line)

                        case "{http://www.w3.org/2000/svg}polyline":
                            points = shape.attrib.get('points', [])

                            points = points.split()
                            points = [point.split(',') for point in points]
                            points = [tuple(map(int, p)) for p in points]

                            polyline = svgwrite.shapes.Polyline(points=points, 
                                                            stroke=stroke,
                                                            stroke_width=stroke_width,
                                                            stroke_opacity=stroke_opacity,
                                                            fill="none")
                            self.editor.canvas.layers[indx].figures.append(SvgShape("polyline", 
                                                                                    polyline, 
                                                                                    points=points)
                                                                                    )
                            self.editor.canvas.layers[indx].g.add(polyline)

                        case "{http://www.w3.org/2000/svg}polygon":
                            points = shape.attrib.get('points', [])

                            points = points.split()
                            points = [point.split(',') for point in points]
                            points = [tuple(map(int, p)) for p in points]

                            polygon = svgwrite.shapes.Polygon(points=points, 
                                                            stroke=stroke,
                                                            stroke_width=stroke_width,
                                                            stroke_opacity=stroke_opacity,
                                                            fill=fill,
                                                            fill_opacity=fill_opacity)
                            self.editor.canvas.layers[indx].figures.append(SvgShape("polygon", 
                                                                                    polygon, 
                                                                                    points=points)
                                                                                    )
                            self.editor.canvas.layers[indx].g.add(polygon)
                        
                        case "{http://www.w3.org/2000/svg}text":
                            x = int(shape.attrib.get('x', 0))
                            y = int(shape.attrib.get('y', 0))

                            style = shape.attrib['style']
                            font_size = int(style.lstrip("font-size:")[:-1])

                            text = svgwrite.text.Text(text=shape.text, 
                                                        insert=(x, y), 
                                                        fill=fill, 
                                                        opacity=fill_opacity, 
                                                        style=style)
                            self.editor.canvas.layers[indx].figures.append(SvgShape("text", 
                                                                                    text, 
                                                                                    font_size=font_size, 
                                                                                    insert=(x, y))
                                                                                    )
                            self.editor.canvas.layers[indx].g.add(text)

            self.editor.drawer.layer = self.editor.canvas.layers[0]
            self.editor.drawer.layer.setStyleSheet("background: rgba(240,128,128, 1);")
            self.editor.canvas.refresh()

    def on_save_as(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, 
                                                  "Сохранить файл SVG", 
                                                  "", 
                                                  "SVG Files (*.svg);;All Files (*)", 
                                                  options=options)
        
        if filename:
            canvas = self.editor.canvas
            draw: Drawer = self.editor.drawer
            if draw.selected:
                canvas.dwg.elements.remove(draw.selected.params["selector"])
                draw.selected.params.pop("selector")
                draw.selected = None

            canvas.dwg.filename = filename
            canvas.dwg.save()

    def on_save(self):
        canvas = self.editor.canvas
        draw: Drawer = self.editor.drawer

        if canvas.dwg.filename == "noname.svg":
            options = QFileDialog.Options()
            filename, _ = QFileDialog.getSaveFileName(self, 
                                                      "Сохранить файл SVG", 
                                                      "", 
                                                      "SVG Files (*.svg);;All Files (*)", 
                                                      options=options)
            if not filename:
                return
            
            canvas.dwg.filename = filename

        if draw.selected:
            canvas.dwg.elements.remove(draw.selected.params["selector"])
            draw.selected.params.pop("selector")
            draw.selected = None
            self.editor.canvas.refresh()
        
        canvas.dwg.save()

    def on_close(self):
        self.editor.close()

    def change_stroke_color(self):
        dialog = QColorDialog()
        draw: Drawer = self.editor.drawer

        if draw.selected:
            initial_color = list(map(
                int, draw.selected.obj.attribs.get("stroke", 
                                                   constants["def_stroke"]).strip("rgb")[1:-1].split(", ")
                ))
            initial_opacity = int(float(draw.selected.obj.attribs.get("stroke-opacity", 1)) * 255)
            initial_color.append(initial_opacity)
            color = dialog.getColor(options=QColorDialog.ShowAlphaChannel, initial=QColor(*initial_color))

        else:
            color = dialog.getColor(options=QColorDialog.ShowAlphaChannel)
        
        opacity = color.alphaF()
        color = "rgb" + str(color.getRgb()[:-1])

        if draw.selected:
            draw.selected.obj.attribs["stroke"] = color
            draw.selected.obj.attribs["stroke-opacity"] = opacity
            self.editor.canvas.refresh()
            
        self.stroke_color.setStyleSheet(f"background: {color};")
        self.editor.drawer.stroke = color
        self.editor.drawer.stroke_opacity = opacity

    def change_fill_color(self):
        dialog = QColorDialog()
        draw: Drawer = self.editor.drawer

        if draw.selected:
            initial_color = list(map(
                int, draw.selected.obj.attribs.get("fill", 
                                                   constants["def_fill"]).strip("rgb")[1:-1].split(", ")
                ))
            initial_opacity = int(float(draw.selected.obj.attribs.get("fill-opacity", 1)) * 255)
            initial_color.append(initial_opacity)
            color = dialog.getColor(options=QColorDialog.ShowAlphaChannel, initial=QColor(*initial_color))
        else:
            color = dialog.getColor(options=QColorDialog.ShowAlphaChannel)

        opacity = color.alphaF()
        color = "rgb" + str(color.getRgb()[:-1])

        if draw.selected:
            draw.selected.obj.attribs["fill"] = color
            draw.selected.obj.attribs["fill-opacity"] = opacity
            self.editor.canvas.refresh()

        self.fill_color.setStyleSheet(f"background: {color};")
        self.editor.drawer.fill = color
        self.editor.drawer.fill_opacity = opacity
    
    def change_font_size(self):
        draw: Drawer = self.editor.drawer
        canvas = self.editor.canvas
        val = self.font_size.value()

        figure: SvgShape = draw.selected

        if figure and figure.shape == "text":
            figure.params["font_size"] = val
            figure.obj.attribs["font-size"] = val

            canvas.dwg.elements.remove(figure.params["selector"])
            select_rect = canvas.is_text_clicked(figure, figure.params["insert"])
            canvas.dwg.add(select_rect)
            figure.params["selector"] = select_rect

            canvas.refresh()
    
    def change_stroke_width(self):
        draw: Drawer = self.editor.drawer
        canvas = self.editor.canvas
        figure: SvgShape = draw.selected

        val = self.stroke_w.value()

        draw.width = val

        if figure:
            figure.obj.attribs["stroke-width"] = val

            canvas.refresh()
    
    def to_foreground(self):
        if not self.editor.drawer.selected:
            return
        figure: SvgShape = self.editor.drawer.selected
        layer: Layer = self.editor.drawer.layer
        layer.figures.remove(figure)
        layer.figures.append(figure)
        layer.g.elements.remove(figure.obj)
        layer.g.elements.append(figure.obj)
        self.editor.canvas.refresh()

    def to_background(self):
        if not self.editor.drawer.selected:
            return
        figure: SvgShape = self.editor.drawer.selected
        layer: Layer = self.editor.drawer.layer
        layer.figures.remove(figure)
        layer.figures.insert(0, figure)
        layer.g.elements.remove(figure.obj)
        layer.g.elements.insert(0, figure.obj)
        self.editor.canvas.refresh()


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

        self.add_polyline_btn = QToggleButton("Add polyline", self)
        self.addWidget(self.add_polyline_btn)

        self.add_polygon_btn = QToggleButton("Add polygon", self)
        self.addWidget(self.add_polygon_btn)

        self.add_text_btn = QToggleButton("Add text", self)
        self.addWidget(self.add_text_btn)

        delete_figure = QPushButton("Delete figure", self)
        delete_figure.clicked.connect(self.delete_figure)
        self.addWidget(delete_figure)

        self.add_rect_btn.clicked.connect(lambda: self.add_figure("rect"))
        self.add_circle_btn.clicked.connect(lambda: self.add_figure("circle"))
        self.add_line_btn.clicked.connect(lambda: self.add_figure("line"))
        self.add_polyline_btn.clicked.connect(lambda: self.add_figure("polyline"))
        self.add_polygon_btn.clicked.connect(lambda: self.add_figure("polygon"))
        self.add_text_btn.clicked.connect(lambda: self.add_figure("text"))

        self.buttons: dict[str, QToggleButton] = {"rect": self.add_rect_btn, 
                                             "circle": self.add_circle_btn, 
                                             "line": self.add_line_btn, 
                                             "polyline": self.add_polyline_btn, 
                                             "polygon": self.add_polygon_btn,
                                             "text": self.add_text_btn}

    def add_figure(self, fig_name: str):
        if fig_name in ("polyline, polygon"):
            self.editor.canvas.started_polyline = False

        if self.buttons[fig_name].isChecked():
            self.buttons[fig_name].setChecked(True)
            self.editor.drawer.figure = fig_name
        else:
            self.buttons[fig_name].setChecked(False)
            self.editor.drawer.figure = None
        for button in self.buttons.values():
            if button != self.buttons[fig_name]:
                button.setChecked(False)

    def delete_figure(self):
        self.editor.canvas.delete_figure(self.editor.drawer.selected)


class LayerBar(QToolBar):

    def __init__(self, title, parent):
        super().__init__(title, parent)

        self.editor: QMainWindow = parent

        self.preview = QSvgWidget(self)
        self.preview.setFixedSize(constants["preview_w"], constants["preview_h"])
        self.addWidget(self.preview)
        self.preview.setStyleSheet("background: white; border:5px solid rgba(240,128,128, 0.8);")

        self.add_layer_bnt = QPushButton(parent=self, text="Add layer")
        self.add_layer_bnt.clicked.connect(self.add_layer)
        self.addWidget(self.add_layer_bnt)

        self.del_layer_bnt = QPushButton(parent=self, text="Delete layer")
        self.del_layer_bnt.clicked.connect(self.del_layer)
        self.addWidget(self.del_layer_bnt)
        
        canvas = self.parent().canvas

        main_layer: Layer = Layer(self, "main")
        main_layer.setStyleSheet("background: rgba(240,128,128, 1);")
        canvas.layers.append(main_layer)
        canvas.dwg.add(main_layer.g)
        self.addWidget(main_layer)
    
    def _add_layer(self, name):
        canvas = self.parent().canvas

        layer = Layer(parent=self, name=name)
        canvas.layers.append(layer)
        canvas.dwg.add(layer.g)
        self.addWidget(layer)
    
    def add_layer(self):
        txt, ok = QInputDialog(parent=None).getText(None, 
                                                    "Text input", 
                                                    "Write new layer's name")
        if ok:
            self._add_layer(txt)
            
    def del_layer(self):
        layer: Layer = self.editor.drawer.layer
        if id(layer) != id(self.editor.canvas.layers[0]):
            self.editor.drawer.layer = self.editor.canvas.layers[0]
            self.editor.canvas.dwg.elements.remove(layer.g)
            self.editor.canvas.layers.remove(layer)
            layer.deleteLater() 
