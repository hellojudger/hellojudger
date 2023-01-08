from PyQt6 import QtWidgets, QtGui, QtCore
import json


class ColorChoicer(QtWidgets.QWidget):
    def __init__(self, value:QtGui.QColor, parent=None):
        super().__init__(parent=parent)
        Layout = QtWidgets.QHBoxLayout()
        self.color_inputer = QtWidgets.QLineEdit()
        self.color_inputer.setInputMask("HHHHHH")
        self.color_inputer.setDisabled(True)
        self.setValue(value)
        self.choice_color_button = QtWidgets.QPushButton("...")
        self.choice_color_button.clicked.connect(self.button_clicker)
        Layout.addWidget(self.color_inputer)
        Layout.addWidget(self.choice_color_button)
        self.setLayout(Layout)
    
    def setValue(self, value:QtGui.QColor):
        if value.isValid():
            self.color_inputer.setText(value.name().replace("#", ""))
            self.color_inputer.setStyleSheet("QLineEdit{color: %s;font-weight: bold;}" % value.name())
            self.color_inputer.setToolTip("Hex 颜色：%s\nRGB 颜色：(%d, %d, %d)" % (value.name(), value.red(), value.green(), value.blue()))
     
    def getValue(self) -> QtGui.QColor:
        return QtGui.QColor("#" + self.color_inputer.text())
    
    def button_clicker(self):
        self.setValue(QtWidgets.QColorDialog.getColor(self.getValue(), self, "Hello Judger"))


class StatusColorfulDialog(QtWidgets.QDialog):

    saved = QtCore.pyqtSignal()
    canceled = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        Layout = QtWidgets.QFormLayout()
        self.json_body = json.load(open("settings/status.colorful.json", "r", encoding="utf-8"))
        Layout.addWidget(QtWidgets.QLabel("<h1>评测配色编辑器</h1>"))
        self.widgets = {}
        for i in self.json_body:
            choicer = ColorChoicer(QtGui.QColor(self.json_body[i][0], self.json_body[i][1], self.json_body[i][2]))
            self.widgets[i] = choicer
        for i in self.widgets:
            j = ""
            for k in i:
                if k.isupper():
                    j += " "
                j += k
            j = j[1:]
            Layout.addRow(QtWidgets.QLabel("<b> %s </b>" % j), self.widgets[i])
        self.buttons = QtWidgets.QDialogButtonBox()
        self.buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Reset).clicked.connect(
            self.reset
        )
        self.buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(
            self.save
        )
        self.buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Cancel).clicked.connect(
            self.cancel
        )
        Layout.addWidget(self.buttons)
        self.setLayout(Layout)
        self.setWindowTitle("评测配色编辑器 - Hello Judger")
        self.show()
    
    def reset(self):
        for i in self.json_body:
            self.widgets[i].setValue(QtGui.QColor(self.json_body[i][0], self.json_body[i][1], self.json_body[i][2]))
    
    def save(self):
        for i in self.widgets:
            color = self.widgets[i].getValue()
            if not color.isValid():
                QtWidgets.QMessageBox.critical(self, "Hello Judger", "无法识别 %s 的颜色" % i)
                self.widgets[i].setValue(QtGui.QColor(*self.json_body[i]))
                return
            self.json_body[i] = [color.red(), color.green(), color.blue()]
        json.dump(self.json_body, open("settings/status.colorful.json", "w", encoding="utf-8"))
        self.saved.emit()
        self.close()
    
    def closeEvent(self, a0):
        self.cancel()
        a0.accept()

    def cancel(self):
        self.canceled.emit()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    win = StatusColorfulDialog()
    win.show()
    exit(app.exec())
