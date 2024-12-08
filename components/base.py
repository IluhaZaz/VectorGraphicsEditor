from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication
from PyQt5.QtCore import Qt

from components.svg_utils import Drawer
from components.bars import FiguresBar, ToolBar, LayerBar
from components.canvas import Canvas


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
        