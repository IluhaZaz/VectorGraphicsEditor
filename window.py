import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from components.base import VectorGraphicsEditor, Ui_MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/app_icon.png"))
    
    window = VectorGraphicsEditor()
    ui_setuper = Ui_MainWindow()

    ui_setuper.setup_ui(window) 
    window.show()
    sys.exit(app.exec_())