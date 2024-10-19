import svgwrite
import svgwrite.shapes

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import QByteArray, Qt, QPoint

from components.svg_utils import Drawer, SvgShape


class Canvas(QSvgWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.figures: list[SvgShape] = []

    def add_figure(self, start: tuple[int], end: tuple[int]):
        draw: Drawer = self.parent().drawer

        match draw.figure:
            case "circle":
                r = (((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5)//2
                center = (start[0] + end[0])//2, (start[1] + end[1])//2
                circle = svgwrite.shapes.Circle(center=center, 
                                                r=r, 
                                                stroke=draw.stroke_color, 
                                                stroke_width=draw.width, 
                                                fill = draw.fill,
                                                fill_opacity=draw.fill_opacity,
                                                stroke_opacity=draw.stroke_opacity)
                draw.dwg.add(circle)
                self.figures.append(SvgShape("circle", circle, center=center, r=r))

            case "rect":
                size = (abs(start[0] - end[0]), abs(start[1] - end[1]))
                if start[0] > end[0]:
                    if start[1] > end[1]:
                        top_left = end
                    else:
                        top_left = end[0], start[1]
                else:
                    if start[1] > end[1]:
                        top_left = start[0], end[1]
                    else:
                        top_left = start
                rect = svgwrite.shapes.Rect(insert=top_left,
                                            size=size,
                                            stroke=draw.stroke_color, 
                                            stroke_width=draw.width, 
                                            fill = draw.fill,
                                            fill_opacity=draw.fill_opacity,
                                            stroke_opacity=draw.stroke_opacity)
                draw.dwg.add(rect)
                self.figures.append(SvgShape("rect", rect, insert=top_left, size=size))

            case "line":
                line = svgwrite.shapes.Line(start=start,
                                            end=end,
                                            stroke=draw.stroke_color,
                                            stroke_width=draw.width,
                                            stroke_opacity=draw.stroke_opacity)
                draw.dwg.add(line)
                self.figures.append(SvgShape("line", line, start=start, end=end))
        

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            draw: Drawer = self.parent().drawer

            start = draw.start
            end = event.pos().x(), event.pos().y()

            dist = ((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5
            if dist < 3:
                self.select_figure(event.pos())
                return
            
            # if draw.selected:
            #     figure = self.find_clicked_figure(draw.start)[0]
            #     if figure == draw.selected:
            #         dx = event.pos()[0] - draw.start[0]
            #         dy = event.pos()[1] - draw.start[1]
                    
            #         self.delete_figure()

            self.add_figure(start, end)
                    
            self.parent().canvas.load(QByteArray(draw.dwg.tostring().encode('utf-8')))

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
         self.parent().drawer.start = (event.pos().x(), event.pos().y())

    def find_clicked_figure(self, pos: tuple[int]):

        tolerance = 3
        
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
                    if distance_to_line <= tolerance:
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