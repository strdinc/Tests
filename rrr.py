# test_create_quiz.py

from PyQt5 import QtWidgets
from ui_create_quiz import Ui_CreateQuizDialog  # Импортируем скомпилированный UI


class CreateQuizWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CreateQuizDialog()
        self.ui.setupUi(self)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = CreateQuizWindow()
    window.show()
    sys.exit(app.exec_())