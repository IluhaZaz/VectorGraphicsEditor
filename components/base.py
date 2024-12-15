from json import load, dump
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtCore import Qt

from components.svg_utils import Drawer, LoadingMenu
from components.bars import FiguresBar, ToolBar, LayerBar
from components.canvas import Canvas


with open('constants.json', 'r') as f:
    constants = load(f)

class VectorGraphicsEditor(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.canvas: Canvas
        self.central_widget: QWidget
        self.tool_bar: ToolBar
        self.figures_bar: FiguresBar
        self.layer_bar: LayerBar
        self.drawer: Drawer


class Ui_MainWindow:
    
    def setup_ui(self, main_window: VectorGraphicsEditor):
        main_window.setWindowTitle("VectorCanvas")

        main_window.setWindowState(Qt.WindowFullScreen)

        main_window.central_widget = QWidget()
        main_window.setCentralWidget(main_window.central_widget)

        max_size = QApplication.primaryScreen().size()
        main_window.canvas = Canvas(main_window, (max_size.width() - 10, max_size.height() - 50))
        main_window.canvas.move(10, 50)

        preview_size = max_size.width()//7, max_size.height()//7
        with open("constants.json", 'r+') as f:
            data = load(f)
            data["preview_w"] = preview_size[0]
            data["preview_h"] = preview_size[1]

            f.seek(0)
            dump(data, f, indent=4)

        main_window.tool_bar = ToolBar("Tool bar", parent=main_window)
        main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, main_window.tool_bar)

        main_window.figures_bar = FiguresBar("Figures bar", parent=main_window)
        main_window.addToolBar(Qt.ToolBarArea.RightToolBarArea, main_window.figures_bar)

        main_window.layer_bar = LayerBar("Layer bar", parent=main_window)
        main_window.addToolBar(Qt.ToolBarArea.RightToolBarArea, main_window.layer_bar)
        
        main_window.drawer = Drawer(main_window)

        main_window.central_widget.setStyleSheet("background: rgba(0, 0, 0, 0.8);")
        main_window.canvas.setStyleSheet("background: white; border:5px solid rgba(240,128,128, 0.8);")
        main_window.tool_bar.setStyleSheet("""QToolBar{background: rgba(0, 0, 0, 0.6); border:2px solid rgba(240,128,128, 0.8);}
                                           QPushButton{background: rgba(240,128,128, 0.8);}
                                           ColorTextEdit{background: rgba(240,128,128, 0.8);}
                                           QSlider::handle:horizontal {background: rgba(240,128,128, 0.8); border-radius: 3px;}
                                           """)
        main_window.figures_bar.setStyleSheet("""QToolBar{background: rgba(0, 0, 0, 0.6); border:2px solid rgba(240,128,128, 0.8);}
                                              QPushButton{background: rgba(240,128,128, 0.8)}
                                              """)
        main_window.layer_bar.setStyleSheet("""QToolBar{background: rgba(0, 0, 0, 0.6); border:2px solid rgba(240,128,128, 0.8);}
                                              """)

class LoadingWindow(QMainWindow):
    def __init__(self, main_window, ui_main_setuper):
        super().__init__()

        self.main_window: VectorGraphicsEditor = main_window
        self.ui_main_setuper: Ui_MainWindow = ui_main_setuper

        self.central_widget: QWidget
        self.loading_menu: LoadingMenu
    
    def end_loading(self, size: tuple[int] = None, open_existing: bool = False):
        self.ui_main_setuper.setup_ui(self.main_window)
        self.close()
        self.main_window.show()
        if size and size != (-1, -1):
            if size[0] == -1:
                self.main_window.canvas.setFixedHeight(size[1])
                self.main_window.canvas.dwg.attribs['height'] = size[1]
            elif size[1] == -1:
                self.main_window.canvas.setFixedWidth(size[0])
                self.main_window.canvas.dwg.attribs['width'] = size[0]
            else:
                self.main_window.canvas.setFixedSize(size[0], size[1])
                self.main_window.canvas.dwg.attribs = {'width': size[0], 'height': size[1]}

            preview_size = size[0]//7, size[1]//7
            self.main_window.layer_bar.preview.setFixedSize(*preview_size)

        elif open_existing:
            self.main_window.tool_bar.open()


class Ui_LoadingWindow:
    
    def setup_ui(self, loading_window: LoadingWindow):
        loading_window.setWindowTitle("VectorCanvas - loading_window")

        loading_window.setWindowState(Qt.WindowFullScreen)

        loading_window.central_widget = QWidget()
        loading_window.setCentralWidget(loading_window.central_widget)

        loading_window.loading_menu = LoadingMenu(loading_window)
        max_size = QApplication.primaryScreen().size()
        loading_window.loading_menu.setGeometry((max_size.width() - constants['load_bth_w'])//2, 
                                                (max_size.height() - constants['load_bth_h']*3)//2,
                                                constants['load_bth_w'], 
                                                constants['load_bth_h']*3)

        loading_window.central_widget.setStyleSheet("background: rgba(0, 0, 0, 0.8);border:50px solid rgba(240,128,128, 0.8);")
        loading_window.loading_menu.setStyleSheet("""QWidget{background: rgba(0, 0, 0, 0.6); border:2px solid rgba(240,128,128, 0.8);}
                                                    QPushButton{background: rgba(240,128,128, 0.8);""" + f"width: {constants['load_bth_w']}px; height: {constants['load_bth_h']}px"+  
                                                    ";}"
                                                )
