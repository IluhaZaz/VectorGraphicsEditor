import svgwrite.shapes
import svgwrite.text

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray, QPoint
from PyQt5.QtWidgets import QInputDialog
from json import load

import svgwrite.path
import svgwrite.shapes

from components.svg_utils import Drawer, SvgShape, Layer


with open('constants.json', 'r') as f:
    constants = load(f)

TOLERANCE = constants["tolerance"]

class Canvas(QSvgWidget):

    def __init__(self, parent, size: tuple[int]):
        super().__init__(parent)
        self.setFixedSize(*size)
        self.dwg = svgwrite.Drawing(profile="full", size=size)
        self.layers: list[Layer] = []
        self.started_polyline: bool = False

    def refresh(self, preview: bool = True):
        self.load(QByteArray(self.dwg.tostring().encode('utf-8')))
        if preview:
            svg =  self._make_svg_from_element(self.parent().drawer.layer.g).encode('utf-8')
            self.parent().layer_bar.preview.load(QByteArray(svg))
    
    def get_current_layer(self) -> Layer:
        return self.parent().drawer.layer

    def add_figure(self, start: tuple[int], end: tuple[int]):
        draw: Drawer = self.parent().drawer
        layer: Layer = self.get_current_layer()

        match draw.figure:
            case "circle":
                center = (start[0] + end[0])//2, (start[1] + end[1])//2
                circle = svgwrite.shapes.Circle(center=center, 
                                                r=0, 
                                                stroke=draw.stroke, 
                                                stroke_width=draw.width, 
                                                fill = draw.fill,
                                                fill_opacity=draw.fill_opacity,
                                                stroke_opacity=draw.stroke_opacity)
                layer.g.add(circle)
                layer.figures.append(SvgShape("circle", circle, center=center, r=0))

            case "rect":
                rect = svgwrite.shapes.Rect(insert=start,
                                            size=(0, 0),
                                            stroke=draw.stroke, 
                                            stroke_width=draw.width, 
                                            fill = draw.fill,
                                            fill_opacity=draw.fill_opacity,
                                            stroke_opacity=draw.stroke_opacity)
                layer.g.add(rect)
                layer.figures.append(SvgShape("rect", rect, insert=start, size=(0, 0)))

            case "line":
                line = svgwrite.shapes.Line(start=start,
                                            end=end,
                                            stroke=draw.stroke,
                                            stroke_width=draw.width,
                                            stroke_opacity=draw.stroke_opacity)
                layer.g.add(line)
                layer.figures.append(SvgShape("line", line, start=start, end=(end[0] + 1, end[1] + 1)))
            
            case "polyline":
                if self.started_polyline:
                    layer.figures[-1].obj.points.append(end)
                    layer.figures[-1].params["points"].append(end)

                else:
                    self.started_polyline = True
                    polyline = svgwrite.shapes.Polyline(points=[end],
                                                        stroke=draw.stroke,
                                                        stroke_width=draw.width,
                                                        stroke_opacity=draw.stroke_opacity,
                                                        fill="none")
                    layer.g.add(polyline)
                    layer.figures.append(SvgShape("polyline", polyline, points=[end]))
            
            case "polygon":
                if self.started_polyline:
                    layer.figures[-1].obj.points.append(end)
                    layer.figures[-1].params["points"].append(end)

                else:
                    self.started_polyline = True
                    polygon = svgwrite.shapes.Polygon(points=[end], 
                                                        stroke=draw.stroke,
                                                        stroke_width=draw.width,
                                                        stroke_opacity=draw.stroke_opacity,
                                                        fill = draw.fill,
                                                        fill_opacity=draw.fill_opacity,)
                    layer.g.add(polygon)
                    layer.figures.append(SvgShape("polygon", polygon, points=[end]))
            
            case "text":
                txt, ok = QInputDialog(parent=None).getText(None, "Text input", "Write text to display it")
                if ok:
                    font_size = self.parent().tool_bar.font_size.value()
                    text = svgwrite.text.Text(text=txt, 
                                              insert=draw.start, 
                                              fill=draw.stroke, 
                                              fill_opacity=draw.stroke_opacity,
                                              style=f"font-size:{font_size};")
                    layer.g.add(text)
                    layer.figures.append(SvgShape("text", text, insert=draw.start, font_size=font_size))
    
    def _make_svg_from_element(self, element):
        start: str = f"""<?xml version='1.0' encoding='utf-8' ?>
        <svg baseProfile='full' height='{self.size().height()}' version='1.1' width='{self.size().width()}' xmlns='http://www.w3.org/2000/svg' 
        xmlns:ev='http://www.w3.org/2001/xml-events' xmlns:xlink='http://www.w3.org/1999/xlink'>
        <defs />"""
        return start + element.tostring() + "</svg>"

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        pos = event.pos().x(), event.pos().y()
        self.parent().drawer.start = pos
        self.parent().drawer.prev_pos = event.pos()

        draw: Drawer = self.parent().drawer

        draw.selector_side = self.is_selector_clicked(pos)
        if draw.selected:
            draw.selector_point_indx = self.is_polyline_point_clicked(draw.selected, pos)

        if draw.figure:
            self.add_figure(pos, pos)
        elif draw.selector_side or draw.selector_point_indx is not None:
            pass
        else:
            self.select_figure(event.pos())

        self.refresh()

    def mouseMoveEvent(self, event: QMouseEvent | None):
        draw: Drawer = self.parent().drawer
        layer: Layer = self.get_current_layer()
        if draw.figure:
            figure: SvgShape = layer.figures[-1]
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

            self.refresh()
        
        elif draw.selector_side or draw.selector_point_indx is not None:
            start = draw.prev_pos.x(), draw.prev_pos.y()
            end = event.pos().x(), event.pos().y()
            self.edit_figure(start, end, draw.selector_side)

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

                case "rect" | "text":
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
        self.refresh()

    def is_polyline_clicked(self, figure: SvgShape, pos: tuple[int]):
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
            try:
                distance_to_line = abs(
                    (end[1] - start[1]) * pos[0] - (end[0] - start[0]) * pos[1] + end[0] * start[1] - end[1] * start[0]
                    ) / ((end[1] - start[1])**2 + (end[0] - start[0])**2) ** 0.5
            except ZeroDivisionError:
                continue
            if distance_to_line <= TOLERANCE:
                is_clicked = True

        if is_clicked:
            select_size = br_select[0] - tl_select[0], br_select[1] - tl_select[1]
            select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                    size=select_size,
                                    stroke="blue",
                                    fill="none"
                                    )
        return select_rect
    
    def is_line_clicked(self, figure: SvgShape, pos: tuple[int]):
        start = figure.params['start']
        end = figure.params['end']
        select_rect = None

        distance_to_line = abs(
            (end[1] - start[1]) * pos[0] - (end[0] - start[0]) * pos[1] + end[0] * start[1] - end[1] * start[0]
            ) / ((end[1] - start[1])**2 + (end[0] - start[0])**2) ** 0.5
        if distance_to_line <= TOLERANCE:

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
        return select_rect

    def is_text_clicked(self, figure: SvgShape, pos: tuple[int]):
        select_rect = None
        font_size = figure.params["font_size"]
        text_length = len(figure.obj.text) * font_size * 0.6
        text_height = font_size
        size=(text_length, text_height)
        insert = list(figure.params["insert"])
        insert[1] -= text_height

        if insert[0] <= pos[0] <= insert[0] + size[0] and insert[1] <= pos[1] <= insert[1] + size[1]:
            select_rect = svgwrite.shapes.Rect(insert=insert,
                                        size=size,
                                        stroke="blue",
                                        fill="none"
                                        )
        return select_rect
    
    def is_polygon_clicked(self, figure: SvgShape, pos: tuple[int]):
        select_rect = None

        points = figure.params["points"]
        tl_select = list(points[0])
        br_select = list(points[0])

        num_points = len(points)

        if num_points < 3:
            select_rect = self.is_polyline_clicked(figure, (pos[0], pos[1]))
            return select_rect
            
        result = False
        j = num_points - 1
        for i in range(num_points):

            pi = points[i]
            pj = points[j]

            tl_select[0] = min(tl_select[0], pi[0])
            tl_select[1] = min(tl_select[1], pi[1])

            br_select[0] = max(br_select[0], pi[0])
            br_select[1] = max(br_select[1], pi[1])

            if ((pi[1] > pos[1]) != (pj[1] > pos[1])) and (pos[0] < (pj[0] - pi[0]) * (pos[1] - pi[1]) / (pj[1] - pi[1]) + pi[0]):
                result = not result
            j = i

        if result:
            select_size = br_select[0] - tl_select[0], br_select[1] - tl_select[1]
            select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                    size=select_size,
                                    stroke="blue",
                                    fill="none"
                                    )
        return select_rect
    
    def is_circle_clicked(self, figure: SvgShape, pos: tuple[int]):
        select_rect = None
        
        center = figure.params["center"]
        r = figure.params['r']
        if ((center[0] - pos[0]) ** 2 + (center[1] - pos[1]) ** 2) ** 0.5 <= r:

            tl_select = center[0] - r, center[1] - r
            select_size = (2*r, 2*r)
            select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                    size=select_size,
                                    stroke="blue",
                                    fill="none"
                                    )
        return select_rect
    
    def is_rect_clicked(self, figure: SvgShape, pos: tuple[int]):
        select_rect = None

        top_left = figure.params['insert']
        size = figure.params['size']
        if top_left[0] <= pos[0] <= top_left[0] + size[0] and top_left[1] <= pos[1] <= top_left[1] + size[1]:

            tl_select = top_left[0] - 10, top_left[1] - 10
            select_size = (size[0] + 20, size[1] + 20)
            select_rect = svgwrite.shapes.Rect(insert=tl_select,
                                    size=select_size,
                                    stroke="blue",
                                    fill="none"
                                    )
        return select_rect
            
    def find_clicked_figure(self, pos: QPoint):
        layer: Layer = self.get_current_layer()
        
        select_rect = None
        res_fig = None

        for figure in layer.figures[::-1]:
            match figure.shape:
                case'circle':
                    select_rect = self.is_circle_clicked(figure, (pos.x(), pos.y()))
                    if select_rect:
                        res_fig = figure
                        break

                case 'rect':
                    select_rect = self.is_rect_clicked(figure, (pos.x(), pos.y()))
                    if select_rect:
                        res_fig = figure
                        break

                case 'line':
                    select_rect = self.is_line_clicked(figure, (pos.x(), pos.y()))
                    if select_rect:
                        res_fig = figure
                        break
                case "polyline":
                    select_rect = self.is_polyline_clicked(figure, (pos.x(), pos.y()))
                    if select_rect:
                        res_fig = figure
                        break

                case "polygon":
                    select_rect = self.is_polygon_clicked(figure, (pos.x(), pos.y()))
                    if select_rect:
                        res_fig = figure
                        break
                
                case "text":
                    select_rect = self.is_text_clicked(figure, (pos.x(), pos.y()))
                    if select_rect:
                        res_fig = figure
                        break

        return res_fig, select_rect

    def select_figure(self, pos: QPoint):
        draw: Drawer = self.parent().drawer

        if draw.selected:
            self.dwg.elements.remove(draw.selected.params["selector"])
            draw.selected.params.pop("selector")
            draw.selected = None

        figure, select_rect = self.find_clicked_figure(pos)

        if select_rect:
            draw.selected = figure
            self.dwg.add(select_rect)
            draw.selected.params["selector"] = select_rect

            self.parent().tool_bar.stroke_color.setStyleSheet(
                f"background: {figure.obj.attribs.get('stroke', constants['def_stroke'])};"
                )
            self.parent().tool_bar.fill_color.setStyleSheet(
                f"background: {figure.obj.attribs.get('fill', constants['def_fill'])};"
                )
            
        self.refresh()

    def is_selector_clicked(self, pos: tuple[int]):
        draw: Drawer = self.parent().drawer
        if not draw.selected:
            return None
        
        select_rect: svgwrite.shapes.Rect = draw.selected.params["selector"]
        x = select_rect.attribs["x"]
        y = select_rect.attribs["y"]
        w = select_rect.attribs["width"]
        h = select_rect.attribs["height"]

        lines = {}

        lines["top"] = ((x, y), (x + w, y))
        lines["right"] = ((x + w, y), (x + w, y + h))
        lines["bottom"] = ((x + w, y + h), (x, y + h))
        lines["left"] = ((x, y + h), (x, y))

        for key, val in lines.items():
            start, end = val
            distance_to_line = abs(
                (end[1] - start[1]) * pos[0] - (end[0] - start[0]) * pos[1] + end[0] * start[1] - end[1] * start[0]
                ) / ((end[1] - start[1])**2 + (end[0] - start[0])**2) ** 0.5
            if distance_to_line <= TOLERANCE:
                return key
        return None
    
    def is_polyline_point_clicked(self, figure: SvgShape, pos: tuple[int]):
        if figure.shape not in ("polyline", "polygon"):
            return None
        for indx, point in enumerate(figure.params["points"]):
            left = (point[0] - pos[0])**2 + (point[1] - pos[1])**2
            if left <= TOLERANCE**2:
                return indx
        return None

    def edit_circle(self, figure: SvgShape, select_rect, dx: int, dy: int, side: str):
        if side in ("top", "bottom"):                    
            if side == "bottom":
                if figure.params["r"] + dy <= 0:
                    return
                select_rect.attribs["x"] -= dy
                select_rect.attribs["y"] -= dy

                select_rect.attribs["width"] += 2*dy
                select_rect.attribs["height"] += 2*dy

                figure.obj.attribs["r"] += dy
                figure.params["r"] += dy
            else:
                if figure.params["r"] - dy <= 0:
                    return
                select_rect.attribs["x"] += dy
                select_rect.attribs["y"] += dy

                select_rect.attribs["width"] -= 2*dy
                select_rect.attribs["height"] -= 2*dy

                figure.obj.attribs["r"] -= dy
                figure.params["r"] -= dy

        elif side in ("left", "right"):
            
            if side == "right":
                if figure.params["r"] + dx <= 0:
                    return
                select_rect.attribs["x"] -= dx
                select_rect.attribs["y"] -= dx

                select_rect.attribs["width"] += 2*dx
                select_rect.attribs["height"] += 2*dx

                figure.obj.attribs["r"] += dx
                figure.params["r"] += dx
            else:
                if figure.params["r"] - dx <= 0:
                    return
                select_rect.attribs["x"] += dx
                select_rect.attribs["y"] += dx

                select_rect.attribs["width"] -= 2*dx
                select_rect.attribs["height"] -= 2*dx

                figure.obj.attribs["r"] -= dx
                figure.params["r"] -= dx

    def edit_rect(self, figure: SvgShape, select_rect, dx: int, dy: int, side: str):
        if side in ("top", "bottom"):                    
            if side == "bottom":
                if figure.obj.attribs["height"] + dy <= 0:
                    return
                figure.params["size"] = figure.params["size"][0], figure.params["size"][1] + dy
                figure.obj.attribs["height"] += dy
                select_rect.attribs["height"] += dy
            else:
                if figure.obj.attribs["height"] - dy <= 0:
                    return
                figure.params["size"] = figure.params["size"][0], figure.params["size"][1] - dy
                figure.params["insert"] = figure.params["insert"][0], figure.params["insert"][1] + dy
                figure.obj.attribs["y"] += dy
                figure.obj.attribs["height"] -= dy
                select_rect.attribs["y"] += dy
                select_rect.attribs["height"] -= dy

        elif side in ("left", "right"):
            
            if side == "right":
                if figure.obj.attribs["width"] + dx <= 0:
                    return
                figure.params["size"] = figure.params["size"][0] + dx, figure.params["size"][1]
                figure.obj.attribs["width"] += dx
                select_rect.attribs["width"] += dx
            else:
                if figure.obj.attribs["width"] - dx <= 0:
                    return
                figure.params["size"] = figure.params["size"][0] - dx, figure.params["size"][1]
                figure.params["insert"] = figure.params["insert"][0] + dx, figure.params["insert"][1]
                figure.obj.attribs["x"] += dx
                figure.obj.attribs["width"] -= dx
                select_rect.attribs["x"] += dx
                select_rect.attribs["width"] -= dx

    def edit_line(self, figure: SvgShape, select_rect, start: tuple[int], end: tuple[int]):
        center = figure.params["end"]
        left = (center[0] - start[0])**2 + (center[1] - start[1])**2

        is_changed: bool = False
        if left <= TOLERANCE**2:
            is_changed = True

            figure.obj.attribs["x2"] = end[0]
            figure.obj.attribs["y2"] = end[1]
            figure.params["end"] = end

        center = figure.params["start"]
        left = (center[0] - start[0])**2 + (center[1] - start[1])**2
        if left <= TOLERANCE**2:
            is_changed = True

            figure.obj.attribs["x1"] = end[0]
            figure.obj.attribs["y1"] = end[1]
            figure.params["start"] = end
        
        if is_changed:
            select_rect = self.is_line_clicked(figure, end)
            self.dwg.elements.remove(figure.params["selector"])
            figure.params["selector"] = select_rect
            self.dwg.add(select_rect)
    
    def edit_polyline(self, figure: SvgShape, select_rect, end: tuple[int], indx: int):
        if indx is not None:
            points = list(figure.params["points"])
            points[indx] = end
            figure.params["points"] = points
            figure.obj.points = points

            points = [str(p[0]) + "," + str(p[1]) for p in points]
            points = " ".join(points)
            figure.obj.attribs["points"] = points

            select_rect = self.is_polyline_clicked(figure, end)
            self.dwg.elements.remove(figure.params["selector"])
            figure.params["selector"] = select_rect
            self.dwg.add(select_rect)

    def edit_figure(self, start: tuple[int], end: tuple[int], side: str):
        draw: Drawer = self.parent().drawer
        select_rect = draw.selected.params["selector"]

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        figure = draw.selected

        match figure.shape:
            case "circle":
                self.edit_circle(figure, select_rect, dx, dy, side)

            case "rect":
                self.edit_rect(figure, select_rect, dx, dy, side)

            case "line":
                self.edit_line(figure, select_rect, start, end)
            
            case "polyline" | "polygon":
                self.edit_polyline(figure, select_rect, end, draw.selector_point_indx)

    def delete_figure(self, figure: SvgShape):
        draw: Drawer = self.parent().drawer
        layer: Layer = self.get_current_layer()

        if draw.selected is not None:
            self.dwg.elements.remove(draw.selected.params["selector"])
            layer.g.elements.remove(figure.obj)
            layer.figures.remove(figure)
            draw.selected = None
            draw.selector_point_indx = None
            draw.selector_side = None

        self.refresh()
