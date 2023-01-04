import os
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
import base64

class MonacoEditor(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load(QUrl.fromLocalFile(os.path.abspath("resources/editor.html")))

    def getValue(self, callback):
        self.page().runJavaScript("monaco.editor.getModels()[0].getValue()", callback)
    
    def setValue(self, data):
        data = base64.b64encode(data.encode())
        data = data.decode()
        self.page().runJavaScript("monaco.editor.getModels()[0].setValue(Base64.decode('{}'))".format(data))

    def changeLanguage(self, language):
        self.page().runJavaScript("monaco.editor.setModelLanguage(monaco.editor.getModels()[0],'{}')".format(language))

    def contextMenuEvent(self, a0):
        a0.ignore()

class SimpleMonacoEditorDialog(QtWidgets.QDialog):

    saved = pyqtSignal(str)
    canceled = pyqtSignal(str)

    def __init__(self, title = "Hello World", language = "cpp", value = "", parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(title + " - Hello Judger")
        self.buttons = QtWidgets.QDialogButtonBox()
        self.buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(
            lambda: self.editor.getValue(lambda x: self.saved.emit(x))
        )
        self.buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Cancel).clicked.connect(
            lambda: self.editor.getValue(lambda x: self.canceled.emit(x))
        )
        self.Layout = QtWidgets.QVBoxLayout()
        self.title = QtWidgets.QLabel("<h1>%s</h1>" % title)
        self.editor = MonacoEditor()
        self.Layout.addWidget(self.title)
        self.Layout.addWidget(self.editor)
        self.Layout.addWidget(self.buttons)
        self.setLayout(self.Layout)
        def _ytxy_ak_ioi():
            self.editor.changeLanguage(language)
            self.editor.setValue(value)
        self.editor.page().loadFinished.connect(_ytxy_ak_ioi)

class SimpleFileEidtorDialog(SimpleMonacoEditorDialog):
    fn = ""
    def __init__(self, title = "", file = "", parent = None):
        self.fn = file = os.path.abspath(file).replace("\\", "/")
        type_ = os.path.splitext(file)[1].replace(".", "")
        if type_ == "":
            type_ = "plaintext"
        if type_ == "md":
            type_ = "markdown"
        content = ""
        if not os.path.isfile(file):
            with open(file, "w") as f:
                pass
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        super().__init__(title, type_, content, parent)
        self.show()
        self.saved.connect(self.saveAction)
        self.canceled.connect(self.cancelAction)

    def saveAction(self, content):
        with open(self.fn, "w", encoding="utf-8") as f:
            f.write(content)
        self.close()

    def cancelAction(self, content):
        self.close()
