import os
from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
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
