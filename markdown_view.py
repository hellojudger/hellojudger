import os
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import markdown
import json
import darkdetect

ui_theme_json = json.load(open("settings/ui_theme.json", "r", encoding="utf-8"))
theme = ui_theme_json.get("theme", "dark")

if theme == "auto":
    if darkdetect.isLight():
        theme = "light"
    else:
        theme = "dark"

class MarkdownView(QWebEngineView):
    def __init__(self,parent=None):
        super().__init__(parent)
        if theme == "dark":
            self.load(QUrl.fromLocalFile(os.path.abspath("resources/markdown_dark.html")))
        else:
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
        if theme == "dark":
            self.page().setBackgroundColor(QtGui.QColor("black"))

    def contextMenuEvent(self, a0):
        a0.ignore()
