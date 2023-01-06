from PyQt6 import QtWidgets
from simhash import Simhash
import os
import json
import markdown
from bs4 import BeautifulSoup
from itertools import groupby as unique
import jieba


with open("resources/hit_stopwords.txt", "r", encoding="utf-8") as f:
    stop_words = f.readlines()

def hamming_distance(a, b):
    a = bin(a)
    b = bin(b)
    ret = 0
    for i in range(0, min(len(a), len(b))):
        if a[i] != b[i]:
            ret += 1
    return ret

def similarity(a, b):
    dis = hamming_distance(a, b)
    return 1.0 - float(dis) / float(max(len(bin(a)), len(bin(b))))

HASHINGS = os.path.abspath("problem_hashings").replace("\\", "/")

def markdown_clean(md):
    html = markdown.markdown(md)
    html = "<body>"+html+"</body>"
    soup = BeautifulSoup(html, "html.parser")
    return soup.body.text.replace(" ","").replace("\n", "").replace("\t", "")

class OJSearcherDialog(QtWidgets.QDialog):
    def __init__(self, content, parent=None):
        super().__init__(parent=parent)
        content = markdown_clean(content)
        for i in stop_words:
            content = content.replace(i.replace("\n", ""), "")
        content_fz = jieba.lcut(content)
        content_fzed = []
        for i in content_fz:
            if i not in stop_words:
                content_fzed.append(i)
        content = content_fzed
        QtWidgets.QMessageBox.information(self, "Hello Judger", "欢迎使用 OJ 题面搜索！\nOJ 题面搜索使用相似哈希(SimHash)算法做到快速匹配，但由于诸多原因，准确率并不高，敬请谅解。")
        self.content_hash = Simhash(content, 128).value
        Layout = QtWidgets.QFormLayout()
        self.oj_choicer = QtWidgets.QComboBox()
        self.oj_choicer.addItems(list(map(lambda x:x[0], unique(list(map(lambda x:str(x).rsplit('.', 1)[0], os.listdir(HASHINGS)))))))
        self.show_cnt_inputer = QtWidgets.QSpinBox()
        self.show_cnt_inputer.setMaximum(100)
        self.show_cnt_inputer.setMinimum(1)
        self.show_cnt_inputer.setValue(10)
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "题目名", "相似度"])
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 100)
        self.progress = QtWidgets.QProgressBar()
        self.button = QtWidgets.QPushButton("搜索")
        self.button.clicked.connect(self.search)
        Layout.addWidget(QtWidgets.QLabel("<h1>OJ 题面搜索</h1>"))
        Layout.addRow(QtWidgets.QLabel("<b>OJ</b>"), self.oj_choicer)
        Layout.addRow(QtWidgets.QLabel("<b>显示题目个数</b>"), self.show_cnt_inputer)
        Layout.addWidget(self.button)
        Layout.addRow(QtWidgets.QLabel("<b>进度</b>"), self.progress)
        Layout.addWidget(self.table)
        Layout.addWidget(QtWidgets.QLabel("<b>相似度小于 80% 的结果大概率不准，会标成灰色斜体，这些结果仅作为参考。</b>"))
        self.setLayout(Layout)
        self.show()
        self.setFixedSize(640, 480)
        self.setWindowTitle("OJ 题面搜索 - Hello Judger")
        self.exec()
        
    def search(self):
        self.progress.setValue(0)
        pth = os.path.join(HASHINGS, self.oj_choicer.currentText()).replace("\\", "/") + ".json"
        data = json.load(open(pth, "r", encoding="utf-8"))
        self.progress.setRange(0, len(data))
        tops = []
        for j, i in data.items():
            value = {"name": i["name"], "hash": i["hash"], "id": j}
            tops.append(value)
            def cmp(x):
                return similarity(x["hash"], self.content_hash)
            tops.sort(key=cmp)
            tops.reverse()
            self.table.clear()
            self.table.setHorizontalHeaderLabels(["ID", "题目名", "相似度"])
            for k in range(min(len(tops), self.show_cnt_inputer.value(), len(data))):
                self.table.setRowCount(k+1)
                if similarity(tops[k]["hash"], self.content_hash) >= 0.8:
                    self.table.setCellWidget(k, 0, QtWidgets.QLabel(tops[k]["id"]))
                    self.table.setCellWidget(k, 1, QtWidgets.QLabel(tops[k]["name"]))
                    self.table.setCellWidget(k, 2, QtWidgets.QLabel("%.2f%%" % (similarity(tops[k]["hash"], self.content_hash) * 100)))
                else:
                    def glabel(x):
                        return QtWidgets.QLabel("<i style='color:grey'>"+x+"</i>")
                    self.table.setCellWidget(k, 0, glabel(tops[k]["id"]))
                    self.table.setCellWidget(k, 1, glabel(tops[k]["name"]))
                    self.table.setCellWidget(k, 2, glabel("%.2f%%" % (similarity(tops[k]["hash"], self.content_hash) * 100)))
            self.progress.setValue(self.progress.value()+1)
            QtWidgets.QApplication.processEvents()
        self.progress.setValue(self.progress.maximum())
        QtWidgets.QMessageBox.information(self, "Hello Judger", "搜索完成！")

