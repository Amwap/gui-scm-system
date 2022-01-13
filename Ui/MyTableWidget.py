from PyQt5 import QtCore, QtGui, QtWidgets


class TableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        self.mouse_press = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_press = "mouse left press"
        elif event.button() == QtCore.Qt.RightButton:
            self.mouse_press = "mouse right press"
        elif event.button() == QtCore.Qt.MidButton:
            self.mouse_press = "mouse middle press"
        super(TableWidget, self).mousePressEvent(event)