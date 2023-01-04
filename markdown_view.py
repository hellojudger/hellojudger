import os
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import markdown

class MarkdownView(QWebEngineView):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.load(QUrl.fromLocalFile(os.path.abspath("resources/markdown.html")))

    def setValue(self, md):
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.tables'
        ]
        body_html = markdown.markdown(md, extensions=extensions)
        self.page().runJavaScript("document.getElementById(\"body\").innerHTML=%s;make_latex();no_link();" % repr(body_html))
    
    def contextMenuEvent(self, a0):
        a0.ignore()
