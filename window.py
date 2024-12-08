import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from components.base import VectorGraphicsEditor, Ui_MainWindow, LoadingWindow, Ui_LoadingWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/app_icon.png"))
    
    main_window = VectorGraphicsEditor()
    ui_main_setuper = Ui_MainWindow()

    window = LoadingWindow(main_window, ui_main_setuper)
    ui_setuper = Ui_LoadingWindow()

    ui_setuper.setup_ui(window) 
    window.show()
    sys.exit(app.exec_())
    