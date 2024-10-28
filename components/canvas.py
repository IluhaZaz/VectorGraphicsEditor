import svgwrite
import svgwrite.shapes

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray, Qt, QPoint
from copy import copy
from json import load

from components.svg_utils import Drawer, SvgShape


with open('constants.json', 'r') as f:
    constants = load(f)

TOLERANCE = constants["tolerance"]

class Canvas(QSvgWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.figures: list[SvgShape] = []
        self.points: list[int] = []

    def add_figure(self, start: tuple[int], end: tuple[int]):
        draw: Drawer = self.parent().drawer

        match draw.figure:
            case "circle":
                center = (start[0] + end[0])//2, (start[1] + end[1])//2
                circle = svgwrite.shapes.Circle(center=center, 
                                                r=0, 
                                                stroke=draw.stroke_color, 
                                                stroke_width=draw.width, 
                                                fill = draw.fill,
                                                fill_opacity=draw.fill_opacity,
                                                stroke_opacity=draw.stroke_opacity)
                draw.dwg.add(circle)
                self.figures.append(SvgShape("circle", circle, center=center, r=0))

            case "rect":
                rect = svgwrite.shapes.Rect(insert=start,
                                            size=(0, 0),
                                            stroke=draw.stroke_color, 
                                            stroke_width=draw.width, 
                                            fill = draw.fill,
                                            fill_opacity=draw.fill_opacity,
                                            stroke_opacity=draw.stroke_opacity)
                draw.dwg.add(rect)
                self.figures.append(SvgShape("rect", rect, insert=start, size=(0, 0)))

            case "line":
                line = svgwrite.shapes.Line(start=start,
                                            end=end,
                                            stroke=draw.stroke_color,
                                            stroke_width=draw.width,
                                            stroke_opacity=draw.stroke_opacity)
                draw.dwg.add(line)
                self.figures.append(SvgShape("line", line, start=start, end=(end[0] + 1, end[1] + 1)))
            
            case "polyline":
                if self.points:
                    draw.dwg.elements.remove(self.figures.pop(-1).obj)
                self.points.append(end)

                polyline = svgwrite.shapes.Polyline(points=self.points, 
                                                    stroke=draw.stroke_color,
                                                    stroke_width=draw.width,
                                                    stroke_opacity=draw.stroke_opacity,
                                                    fill="none")
                draw.dwg.add(polyline)
                self.figures.append(SvgShape("polyline", polyline, points=copy(self.points)))
            
            case "polygon":
                if self.points:
                    draw.dwg.elements.remove(self.figures.pop(-1).obj)
                self.points.append(end)

                polygon = svgwrite.shapes.Polygon(points=self.points, 
                                                    stroke=draw.stroke_color,
                                                    stroke_width=draw.width,
                                                    stroke_opacity=draw.stroke_opacity,
                                                    fill = draw.fill,
                                                    fill_opacity=draw.fill_opacity,)
                draw.dwg.add(polygon)
                self.figures.append(SvgShape("polygon", polygon, points=copy(self.points)))

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        pos = event.pos().x(), event.pos().y()
        self.parent().drawer.start = pos
        self.parent().drawer.prev_pos = event.pos()

        draw: Drawer = self.parent().drawer

        if draw.figure:
            self.add_figure(pos, pos)
        else:
            self.select_figure(event.pos())

        self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))

    def mouseMoveEvent(self, event: QMouseEvent | None):
        draw: Drawer = self.parent().drawer
        if draw.figure:
            figure: SvgShape = self.figures[-1]
            dx = event.pos().x() - draw.start[0]
            dy = event.pos().y() - draw.start[1]
            match(figure.shape):
                case "circle":
                    figure.params["r"] = (dx**2 + dy**2)**(0.5)
                    figure.obj.attribs["r"] = (dx**2 + dy**2)**(0.5)

                case "rect":
                    if dx >= 0 and dy >= 0:
                        figure.obj.attribs["width"] = dx
                        figure.obj.attribs["height"] = dy
                        figure.params["size"] = (dx, dy)
                    elif dx >= 0 and dy <= 0:
                        figure.obj.attribs["y"] = draw.start[1] + dy
                        figure.obj.attribs["width"] = dx
                        figure.obj.attribs["height"] = -dy

                        figure.params["insert"] = draw.start[0], figure.obj.attribs["y"]
                        figure.params["size"] = (dx, -dy)

                    elif dx <= 0 and dy >= 0:
                        figure.obj.attribs["x"] = draw.start[0] + dx
                        figure.obj.attribs["width"] = -dx
                        figure.obj.attribs["height"] = dy

                        figure.params["insert"] = figure.obj.attribs["x"], draw.start[1]
                        figure.params["size"] = (-dx, dy)

                    else:
                        figure.obj.attribs["x"] = draw.start[0] + dx
                        figure.obj.attribs["y"] = draw.start[1] + dy
                        figure.obj.attribs["width"] = -dx
                        figure.obj.attribs["height"] = -dy

                        figure.params["insert"] = figure.obj.attribs["x"], figure.obj.attribs["y"]
                        figure.params["size"] = (-dx, -dy)

                case "line":
                    figure.obj.attribs["x2"] = event.pos().x()
                    figure.obj.attribs["y2"] = event.pos().y()

                    figure.params["end"] = figure.obj.attribs["x2"], figure.obj.attribs["y2"]

            self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))

        elif draw.selected:
            figure = draw.selected

            dx = event.pos().x() - draw.prev_pos.x()
            dy = event.pos().y() - draw.prev_pos.y()
            
            match(figure.shape):

                case "circle":
                    center = figure.params["center"]

                    figure.params["center"] = (center[0] + dx, center[1] + dy)
                    figure.obj.attribs["cx"] +=dx
                    figure.obj.attribs["cy"] +=dy

                case "rect":
                    insert = figure.params["insert"]

                    figure.params["insert"] = (insert[0] + dx, insert[1] + dy)
                    figure.obj.attribs["x"] = insert[0] + dx
                    figure.obj.attribs["y"] = insert[1] + dy
                
                case "line":

                    start = figure.params["start"]
                    figure.params["start"] = (start[0] + dx, start[1] + dy)
                    end = figure.params["end"]
                    figure.params["end"] = (end[0] + dx, end[1] + dy)

                    figure.obj.attribs["x1"] += dx
                    figure.obj.attribs["y1"] += dy
                    figure.obj.attribs["x2"] += dx
                    figure.obj.attribs["y2"] += dy
                
                case "polyline" | "polygon":

                    points = figure.params["points"]

                    for i in range(len(points)):
                        points[i] = (points[i][0] + dx, points[i][1] + dy)

                    figure.obj.points = points
                    points = [str(p) for p in points]
                    figure.obj.attribs["points"] = " ".join(points)

            figure.params["selector"].attribs["x"] += dx
            figure.params["selector"].attribs["y"] += dy
            
            draw.prev_pos = event.pos()
            self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))

    def is_polyline_clicked(self, figure: SvgShape, pos: QPoint):
        select_rect = None

        points = figure.params["points"]

        tl_select = list(points[0])
        br_select = list(points[0])
        is_clicked = False

        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]

            tl_select[0] = min(tl_select[0], end[0])
            tl_select[1] = min(tl_select[1], end[1])

            br_select[0] = max(br_select[0], end[0])
            br_select[1] = max(br_select[1], end[1])

            distance_to_line = abs((end[1] - start[1]) * pos.x() - (end[0] - start[0]) * pos.y() + end[0] * start[1] - end[1] * start[0]) / ((end[1] - start[1])**2 + (end[0] - start[0])**2) ** 0.5
            if distance_to_line <= TOLERANCE:
                print(f"Polyine selected: points={points}")
                is_clicked = True
        if is_clicked:
            select_size = br_select[0] - tl_select[0], br_select[1] - tl_select[1]
            select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                    size=select_size,
                                    stroke="blue",
                                    fill="none"
                                    )
        return figure, select_rect
            
    def find_clicked_figure(self, pos: QPoint):
        
        tl_select, select_size = None, None
        select_rect = None
        res_fig = None

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
                        res_fig = figure
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

                        res_fig = figure
                        break

                case 'line':
                    start = figure.params['start']
                    end = figure.params['end']

                    distance_to_line = abs((end[1] - start[1]) * pos.x() - (end[0] - start[0]) * pos.y() + end[0] * start[1] - end[1] * start[0]) / ((end[1] - start[1])**2 + (end[0] - start[0])**2) ** 0.5
                    if distance_to_line <= TOLERANCE:
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

                        res_fig = figure
                        break
                case "polyline":
                    res_fig, select_rect = self.is_polyline_clicked(figure, pos)
                    break

                case "polygon":
                    points = figure.params["points"]
                    tl_select = list(points[0])
                    br_select = list(points[0])

                    num_points = len(points)

                    if num_points < 3:
                        res_fig, select_rect = self.is_polyline_clicked(figure, pos)
                        break
                        
                    result = False
                    j = num_points - 1
                    for i in range(num_points):

                        pi = points[i]
                        pj = points[j]

                        tl_select[0] = min(tl_select[0], pi[0])
                        tl_select[1] = min(tl_select[1], pi[1])

                        br_select[0] = max(br_select[0], pi[0])
                        br_select[1] = max(br_select[1], pi[1])

                        if ((pi[1] > pos.y()) != (pj[1] > pos.y())) and (pos.x() < (pj[0] - pi[0]) * (pos.y() - pi[1]) / (pj[1] - pi[1]) + pi[0]):
                            result = not result
                        j = i

                    if result:
                        res_fig = figure
                        select_size = br_select[0] - tl_select[0], br_select[1] - tl_select[1]
                        select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                                size=select_size,
                                                stroke="blue",
                                                fill="none"
                                                )
                        break

        return res_fig, select_rect

    def select_figure(self, pos: QPoint):
        draw: Drawer = self.parent().drawer

        if draw.selected:
            draw.dwg.elements.remove(draw.selected.params["selector"])
            draw.selected.params.pop("selector")
            draw.selected = None

        figure, select_rect = self.find_clicked_figure(pos)

        if select_rect:
            draw.selected = figure
            draw.dwg.add(select_rect)
            draw.selected.params["selector"] = select_rect
            
        self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))

    def delete_figure(self, figure: SvgShape):
        draw: Drawer = self.parent().drawer
        if draw.selected is not None:
            draw.dwg.elements.remove(draw.selected.params["selector"])
            draw.dwg.elements.remove(figure.obj)
            self.figures.remove(figure)
            draw.selected = None

        self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))