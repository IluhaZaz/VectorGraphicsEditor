import sys

from PyQt5.QtWidgets import QApplication

from components.base import VectorGraphicsEditor, Ui_MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VectorGraphicsEditor()
    ui_setuper = Ui_MainWindow()

    ui_setuper.setup_ui(window) 
    window.show()
    sys.exit(app.exec_())