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

class StatusChineseDialog(QtWidgets.QDialog):

    saved = QtCore.pyqtSignal()
    canceled = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        Layout = QtWidgets.QFormLayout()
        self.json_body = json.load(open("settings/status.chinese.json", "r", encoding="utf-8"))
        Layout.addWidget(QtWidgets.QLabel("<h1>中文状态配置编辑器</h1>"))
        self.widgets = {}
        self.is_enabled = QtWidgets.QComboBox()
        self.is_enabled.addItems(["是", "否"])
        self.is_enabled.setCurrentIndex(int(not self.json_body["enabled"]))
        Layout.addRow(QtWidgets.QLabel("<b>是否启用</b>"), self.is_enabled)
        for i in self.json_body.get("content", []):
            choicer = QtWidgets.QLineEdit(self.json_body["content"][i])
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
        self.is_enabled.setCurrentIndex(int(not self.json_body["enabled"]))
        for i in self.json_body.get("content", []):
            self.widgets[i].setText(self.json_body["content"][i])
    
    def save(self):
        for i in self.widgets:
            color = self.widgets[i].text()
            self.json_body["content"][i] = color
        self.json_body["enabled"] = self.is_enabled.currentText() == "是"
        json.dump(self.json_body, open("settings/status.chinese.json", "w", encoding="utf-8"))
        self.saved.emit()
        self.close()
    
    def closeEvent(self, a0):
        self.cancel()
        a0.accept()

    def cancel(self):
        self.canceled.emit()
        self.close()

def UiThemeDialog(parent=None):
    value,_ = QtWidgets.QInputDialog.getItem(parent, "Hello Judger", "选择主题", ["light", "dark", "auto"], 0)
    if not _:
        return
    json.dump({"theme" : value}, open("settings/ui_theme.json", "w", encoding="utf-8"))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    win = StatusChineseDialog()
    win.show()
    exit(app.exec())
