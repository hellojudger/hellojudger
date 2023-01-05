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

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    a = OJSearcherDialog("""
## 题目描述

小 L 和小 Q 在玩一个策略游戏。

有一个长度为 $n$ 的数组 $A$ 和一个长度为 $m$ 的数组 $B$，在此基础上定义一个大小为 $n \times m$ 的矩阵 $C$，满足 $C_{i j} = A_i \times B_j$。所有下标均从 $1$ 开始。

游戏一共会进行 $q$ 轮，在每一轮游戏中，会事先给出 $4$ 个参数 $l_1, r_1, l_2, r_2$，满足 $1 \le l_1 \le r_1 \le n$、$1 \le l_2 \le r_2 \le m$。

游戏中，小 L 先选择一个 $l_1 \sim r_1$ 之间的下标 $x$，然后小 Q 选择一个 $l_2 \sim r_2$ 之间的下标 $y$。定义这一轮游戏中二人的得分是 $C_{x y}$。

小 L 的目标是使得这个得分尽可能大，小 Q 的目标是使得这个得分尽可能小。同时两人都是足够聪明的玩家，每次都会采用最优的策略。

请问：按照二人的最优策略，每轮游戏的得分分别是多少？

## 输入格式

第一行输入三个正整数 $n, m, q$，分别表示数组 $A$，数组 $B$ 的长度和游戏轮数。

第二行：$n$ 个整数，表示 $A_i$，分别表示数组 $A$ 的元素。

第三行：$m$ 个整数，表示 $B_i$，分别表示数组 $B$ 的元素。

接下来 $q$ 行，每行四个正整数，表示这一次游戏的 $l_1, r_1, l_2, r_2$。

## 输出格式

输出共 $q$ 行，每行一个整数，分别表示每一轮游戏中，小 L 和小 Q 在最优策略下的得分。

## 样例 #1

### 样例输入 #1

```
3 2 2
0 1 -2
-3 4
1 3 1 2
2 3 2 2
```

### 样例输出 #1

```
0
4
```

## 样例 #2

### 样例输入 #2

```
6 4 5
3 -1 -2 1 2 0
1 2 -1 -3
1 6 1 4
1 5 1 4
1 4 1 2
2 6 3 4
2 5 2 3
```

### 样例输出 #2

```
0
-2
3
2
-1
```

## 提示

**【样例解释 \#1】**

这组数据中，矩阵 $C$ 如下：

$$ \begin{bmatrix} 0 & 0 \\ -3 & 4 \\ 6 & -8 \end{bmatrix} $$

在第一轮游戏中，无论小 L 选取的是 $x = 2$ 还是 $x = 3$，小 Q 都有办法选择某个 $y$ 使得最终的得分为负数。因此小 L 选择 $x = 1$ 是最优的，因为这样得分一定为 $0$。

而在第二轮游戏中，由于小 L 可以选 $x = 2$，小 Q 只能选 $y = 2$，如此得分为 $4$。

**【样例 \#3】**

见附件中的 `game/game3.in` 与 `game/game3.ans`。

**【样例 \#4】**

见附件中的 `game/game4.in` 与 `game/game4.ans`。

**【数据范围】**

对于所有数据，$1 \le n, m, q \le {10}^5$，$-{10}^9 \le A_i, B_i \le {10}^9$。对于每轮游戏而言，$1 \le l_1 \le r_1 \le n$，$1 \le l_2 \le r_2 \le m$。

| 测试点编号 | $n, m, q \le$ | 特殊条件 |
|:-:|:-:|:-:|
| $1$ | $200$ | 1, 2 |
| $2$ | $200$ | 1 |
| $3$ | $200$ | 2 |
| $4 \sim 5$ | $200$ | 无 |
| $6$ | $1000$ | 1, 2 |
| $7 \sim 8$ | $1000$ | 1 |
| $9 \sim 10$ | $1000$ | 2 |
| $11 \sim 12$ | $1000$ | 无 |
| $13$ | ${10}^5$ | 1, 2 |
| $14 \sim 15$ | ${10}^5$ | 1 |
| $16 \sim 17$ | ${10}^5$ | 2 |
| $18 \sim 20$ | ${10}^5$ | 无 |

其中，特殊性质 1 为：保证 $A_i, B_i > 0$。  
特殊性质 2 为：保证对于每轮游戏而言，要么 $l_1 = r_1$，要么 $l_2 = r_2$。""")