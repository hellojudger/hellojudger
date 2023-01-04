import os
import os.path
import platform
import shutil
import subprocess
import test
import yaml
from PyQt6 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PyQt6.QtWidgets import QApplication
import compile
import json
import markdown_view
import monaco
import time
import qtmodern.styles
import webbrowser

os.chdir(os.path.dirname(__file__))

compiler_settings = json.load(open("settings/compiler.json", "r", encoding="utf-8"))
PROBLEM_PATH = ""

with open("resources/ready.md", encoding="utf-8", mode="r") as f:
    ready_markdown = f.read()

with open("LICENSE", "r", encoding="utf-8") as f:
    LICENSE = f.read()

with open("resources/UPDATES.md", encoding="utf-8", mode="r") as f:
    UPDATES = f.read()

def system_open_file(fp):
    uplf = platform.system()
    if uplf == 'Darwin':
        subprocess.call(['open', fp])
    elif uplf == 'Linux':
        subprocess.call(['xdg-open', fp])
    else:
        os.startfile(fp)


def system_open_directry(fp):
    uplf = platform.system()
    if uplf == "Linux":
        subprocess.call(["xdg-open", fp])
    else:
        os.system("explorer.exe /n,\"%s\"" % fp.replace("/", "\\"))


def get_time_limit():
    configure = os.path.join(PROBLEM_PATH, "testdata/config.yaml").replace("\\", "/")
    source = yaml.load(open(configure, "r", encoding="utf-8"), Loader=yaml.FullLoader)
    min_time = test.time_iden(source.get("time"), 1145141919810)
    max_time = test.time_iden(source.get("time"), 0)
    for i in source.get("cases", []):
        min_time = min(min_time, test.time_iden(i.get("time"), 1145141919810))
        max_time = min(max_time, test.time_iden(i.get("time"), 0))
    for i in source.get("subtasks", []):
        min_time = min(min_time, test.time_iden(i.get("time"), 1145141919810))
        max_time = min(max_time, test.time_iden(i.get("time"), 0))
        for j in source.get("cases", []):
            min_time = min(min_time, test.time_iden(j.get("time"), 1145141919810))
            max_time = min(max_time, test.time_iden(j.get("time"), 0))
    if min_time == 1145141919810 or max_time == 0:
        return "1s"
    if min_time == max_time:
        return "%.2fs" % min_time
    return "%.2fs ~ %.2fs" % (min_time, max_time)


class QTextBrowser(QtWidgets.QTextBrowser):
    def contextMenuEvent(self, e):
        e.ignore()


class FileEdit(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.Layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(__file__)
        self.choicer = QtWidgets.QPushButton("...")
        self.choicer.clicked.connect(self.choice)
        self.Layout.addWidget(self.label)
        self.Layout.addWidget(self.choicer)
        self.setLayout(self.Layout)

    def choice(self):
        try:
            dire = os.path.dirname(self.label.text())
            if self.label.text().strip().rstrip() == "":
                dire = os.path.dirname(__file__)
            file = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", dire)
            if file[0].strip().rstrip() != "":
                self.label.setText(file[0])
        except:
            pass

    def value(self):
        return self.label.text()


class DirectoryEdit(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.Layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(os.path.dirname(__file__))
        self.choicer = QtWidgets.QPushButton("...")
        self.choicer.clicked.connect(self.choice)
        self.Layout.addWidget(self.label)
        self.Layout.addWidget(self.choicer)
        self.setLayout(self.Layout)

    def choice(self):
        try:
            dire = self.label.text()
            if self.label.text().strip().rstrip() == "":
                dire = os.path.dirname(__file__)
            file = QtWidgets.QFileDialog.getExistingDirectory(None, "选择目录", dire)
            if file.strip().rstrip() != "":
                self.label.setText(file)
        except:
            pass

    def value(self):
        return self.label.text()


class ProblemCreator(QtWidgets.QDialog):
    create_done = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.Layout = QtWidgets.QFormLayout()
        self.statementInputer = FileEdit()
        self.testdataInputer = DirectoryEdit()
        self.problemNameInputer = QtWidgets.QLineEdit("不知名的题目")
        self.timeLimitInputer = QtWidgets.QSpinBox()
        self.timeLimitInputer.setMinimum(0)
        self.timeLimitInputer.setMaximum(60000)
        self.timeLimitInputer.setValue(1000)
        self.exportInputer = DirectoryEdit()
        self.do = QtWidgets.QPushButton("开始创建")
        self.do.clicked.connect(self.create_pro)
        self.Layout.addWidget(QtWidgets.QLabel("<h2>题目创建助手</h2>"))
        self.Layout.addRow(QtWidgets.QLabel("<b>题目名</b>"), self.problemNameInputer)
        self.Layout.addRow(QtWidgets.QLabel("<b>题面</b>"), self.statementInputer)
        self.Layout.addRow(QtWidgets.QLabel("<b>测试点目录</b>"), self.testdataInputer)
        self.Layout.addRow(QtWidgets.QLabel("<b>时间限制(单位:毫秒)</b>"), self.timeLimitInputer)
        self.Layout.addRow(QtWidgets.QLabel("<b>保存目录</b>"), self.exportInputer)
        self.Layout.addWidget(self.do)
        self.setLayout(self.Layout)
        self.setStyleSheet("*{font-family:微软雅黑,sans-serif;}")
        self.setWindowTitle("Hello Judger 题目创建助手")

    def create_pro(self):
        all_ = 5 + len(os.listdir(self.testdataInputer.value()))
        dlg = QtWidgets.QProgressDialog("正在创建……", "取消", 0, all_, self)
        dlg.setWindowTitle("正在创建 - Hello Judger")
        dlg.open()
        value = 0
        joiner = lambda y: os.path.join(self.exportInputer.value(), y).replace("\\", "/")
        try:
            shutil.copyfile(self.statementInputer.value(), joiner("problem_zh.md"))
            value = value + 1
            dlg.setValue(value)
            QApplication.processEvents()
            with open(joiner("problem.yaml"), "w", encoding="utf-8") as f:
                f.write("title: %s\n" % self.problemNameInputer.text())
            value = value + 1
            dlg.setValue(value)
            QApplication.processEvents()
            os.mkdir(joiner("additional_file"))
            value = value + 1
            dlg.setValue(value)
            QApplication.processEvents()
            os.mkdir(joiner("testdata"))
            value = value + 1
            dlg.setValue(value)
            QApplication.processEvents()
            with open(joiner("testdata/config.yaml"), "w", encoding="utf-8") as f:
                f.write("type: default\ntime: %dms\n" % self.timeLimitInputer.value())
            value = value + 1
            dlg.setValue(value)
            QApplication.processEvents()
            for i in os.listdir(self.testdataInputer.value()):
                QApplication.processEvents()
                if dlg.wasCanceled():
                    raise Exception("操作被用户取消")
                name = os.path.join(self.testdataInputer.value(), i).replace("\\", "/")
                value = value + 1
                dlg.setValue(value)
                if not os.path.isfile(name):
                    continue
                shutil.copyfile(name, joiner("testdata/%s" % i))
        except Exception as err:
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "操作时发生异常:\n" + str(err))
            dlg.close()
            return
        dlg.setValue(all_)
        QtWidgets.QMessageBox.information(self, "Hello Judger", "操作完成！")
        dlg.close()
        self.create_done.emit(self.exportInputer.value())
        self.close()


class ProblemJudgingDialog(QtWidgets.QDialog):
    def __init__(self, parent, version, optimization, code):
        self.code = code
        self.version = version
        self.optimization = optimization
        super().__init__(parent=parent)
        self.Layout = QtWidgets.QVBoxLayout()
        self.start_btn = QtWidgets.QPushButton("开始")
        self.start_btn.clicked.connect(self.startJudge)
        self.bottom_card = QtWidgets.QWidget()
        self.bottom_card.Layout = QtWidgets.QHBoxLayout()
        self.logging = QTextBrowser()
        self.logging.append("这里将会出现评测日志\n")
        self.result_table = QtWidgets.QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setSortingEnabled(True)
        self.result_table.setHorizontalHeaderLabels(["测试点", "状态", "得分", "耗时"])
        self.bottom_card.Layout.addWidget(self.result_table)
        self.bottom_card.Layout.addWidget(self.logging)
        self.bottom_card.setLayout(self.bottom_card.Layout)
        self.totalWidget = QtWidgets.QLabel()
        self.Layout.addWidget(self.start_btn)
        self.Layout.addWidget(self.bottom_card)
        self.Layout.addWidget(self.totalWidget)
        self.setFixedSize(800, 400)
        self.setLayout(self.Layout)
        self.setWindowTitle("评测窗口 - Hello Judger")

    def append(self, txt):
        QApplication.processEvents()
        self.logging.append("[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] " + txt)

    def slot(self, type, args):
        QApplication.processEvents()
        if type == "judge_begin":
            self.append("评测开始")
        elif type == "scan_begin":
            self.append("扫描输入输出文件开始")
        elif type == "scan_find_task":
            self.append("扫描到 输入：%s 输出：%s" % (args["input"], args["output"]))
        elif type == "scan_finished":
            self.append("扫描输入文件结束")
        elif type == "cases_begin":
            self.append("Cases 评测开始")
        elif type == "task_begin":
            self.append("测试点 %s/%s 评测开始" % (args["input"], args["output"]))
        elif type == "task_finished":
            self.append("测试点 %s/%s 评测完成,状态为 %s,得分为 %.2f,耗时 %.4fs,消息为 %s" % (
                args["input"], args["output"], args["sta"], args["pts"], args["time"], args["msg"]))
            self.result_table.setRowCount(self.result_table.rowCount() + 1)
            pos = self.result_table.rowCount() - 1
            self.result_table.setCellWidget(pos, 0, QtWidgets.QLabel(" %s/%s " % (args["input"], args["output"])))
            self.result_table.setCellWidget(pos, 1, QtWidgets.QLabel(" %s " % args["sta"]))
            self.result_table.setCellWidget(pos, 2, QtWidgets.QLabel(" %.2f " % args["pts"]))
            self.result_table.setCellWidget(pos, 3, QtWidgets.QLabel(" %.2fs " % args["time"]))
            self.result_table.resizeColumnsToContents()
        elif type == "subtasks_begin":
            self.append("Subtasks 评测开始")
        elif type == "subtask_begin":
            self.append("Subtask #%s 开始" % str(args["id"]))
        elif type == "subtask_ignored":
            self.append("该 Subtask 被忽略")
        elif type == "subtask_finished":
            self.append("Subtask #%s 完成,得分 %.2f" % (str(args["id"]), args["total"]))
        elif type == "subtasks_finished":
            self.append("Subtasks 评测结束")
        elif type == "judge_finished":
            self.append("评测结束")

    JUDGING = False

    def closeEvent(self, a0):
        if not self.JUDGING:
            a0.accept()
        else:
            a0.ignore()

    class JudgingThread(QtCore.QObject):
        message = QtCore.pyqtSignal(str, dict)
        judge_done = QtCore.pyqtSignal()
        errored = QtCore.pyqtSignal(str)
        judge_finished = QtCore.pyqtSignal(float)

        def __init__(self, obj):
            super().__init__()
            self.obj = obj

        def slot(self, typ, arg):
            self.message.emit(typ, arg)

        def run(self, prog):
            global PROBLEM_PATH
            try:
                total = test.judge_problem(os.path.join(PROBLEM_PATH, "testdata/config.yaml").replace("\\", "/"), prog,
                                           self.slot)
                self.judge_finished.emit(total)

            except Exception as e:
                self.errored.emit(str(e))

            self.judge_done.emit()

    def judgeFinished(self, total):
        QApplication.processEvents()
        QtWidgets.QMessageBox.information(self, "Hello Judger", "评测完成！")
        self.totalWidget.setText("总分：<b>%.2f</b>" % total)

    def judgeDone(self):
        self.JUDGING = False

    def errored(self, e):
        print(__import__("traceback").format_exc())
        QtWidgets.QMessageBox.critical(self, "Hello Judger", "评测时发生错误：\n" + str(e))

    def startJudge(self):
        self.JUDGING = True
        self.result_table.clearContents()
        self.result_table.setRowCount(0)
        self.logging.clear()
        QApplication.processEvents()
        self.append("准备编译")
        QApplication.processEvents()
        prog = compile.compile_cpp(self.code, self.version, self.optimization)
        self.append("编译成功")
        QApplication.processEvents()
        thread = self.JudgingThread(self)
        thread.judge_done.connect(self.judgeDone)
        thread.judge_finished.connect(self.judgeFinished)
        thread.message.connect(self.slot)
        thread.errored.connect(self.errored)
        thread.run(prog)


class HelloJudgerWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Hello Judger")
        self.contanier = QtWidgets.QWidget()
        self.contanier.Layout = QtWidgets.QHBoxLayout()
        self.problem_shower = markdown_view.MarkdownView()
        self.problem_shower.page().loadFinished.connect(lambda: self.problem_shower.setValue(ready_markdown))
        self.submiter = QtWidgets.QWidget()
        self.submiter.Layout = QtWidgets.QFormLayout()
        self.time_limit_shower = QtWidgets.QLabel("尚不明确")
        self.submiter.header = QtWidgets.QLabel("<h1>提交代码</h1>")
        self.language_choicer = QtWidgets.QComboBox()
        self.language_choicer.addItems(list(map(lambda x: x["name"], compiler_settings.get("versions", []))))
        self.optimization_choicer = QtWidgets.QComboBox()
        self.optimization_choicer.addItems(list(map(lambda x: x["name"], compiler_settings.get("optimizations", []))))
        self.code_editor = monaco.MonacoEditor()
        self.submit_button = QtWidgets.QPushButton("提交")
        self.submit_button.clicked.connect(self.judgingProblem)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>时间限制</b>"), self.time_limit_shower)
        self.submiter.Layout.addWidget(self.submiter.header)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>语言</b>"), self.language_choicer)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>优化</b>"), self.optimization_choicer)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>代码</b>"), self.code_editor)
        self.submiter.Layout.addWidget(self.submit_button)
        self.submiter.setLayout(self.submiter.Layout)
        self.contanier.Layout.addWidget(self.problem_shower)
        self.contanier.Layout.addWidget(self.submiter)
        self.contanier.Layout.setStretchFactor(self.problem_shower, 7)
        self.contanier.Layout.setStretchFactor(self.submiter, 3)
        self.contanier.setLayout(self.contanier.Layout)
        self.contanier.setDisabled(True)
        self.setCentralWidget(self.contanier)
        self.setStyleSheet("*{font-family:微软雅黑,sans-serif;}")
        self.fileMenu = QtWidgets.QMenu("文件")
        self.openProblemAction = QtGui.QAction("打开题目")
        self.openProblemAction.triggered.connect(self.openProblem)
        self.newProblemAction = QtGui.QAction("新建题目")
        self.newProblemAction.triggered.connect(self.newProblem)
        self.settingMenu = QtWidgets.QMenu("设置")
        self.compileConfigureAction = QtGui.QAction("编译配置")
        self.compileConfigureAction.triggered.connect(lambda : monaco.SimpleFileEidtorDialog("编译配置编辑器", "settings/compiler.json"))
        self.exitAction = QtGui.QAction("退出")
        self.exitAction.triggered.connect(exit)
        self.editMenu = QtWidgets.QMenu("编辑")
        self.showAdditionalFileAction = QtGui.QAction("附加文件")
        self.showAdditionalFileAction.triggered.connect(self.showAdditionalFile)
        self.editProblemStatementAction = QtGui.QAction("题面")
        self.editProblemStatementAction.triggered.connect(self.editProblemStatement)
        self.editJudgingConfigureAction = QtGui.QAction("评测配置")
        self.editJudgingConfigureAction.triggered.connect(self.editJudgingConfigure)
        self.editProblemConfigureAction = QtGui.QAction("题目配置")
        self.editProblemConfigureAction.triggered.connect(self.editProblemConfigure)
        self.helpMenu = QtWidgets.QMenu("帮助")
        self.aboutMenu = QtWidgets.QMenu("关于")
        self.aboutHelloJudgerAction = QtGui.QAction("关于本程序")
        self.aboutHelloJudgerAction.triggered.connect(lambda: QtWidgets.QMessageBox.information(self,
            "关于 Hello Judger",
            "Hello Judger 第三代 1.1 by xiezheyuan."
        ))
        self.aboutQtAction = QtGui.QAction("关于 Qt")
        self.aboutQtAction.triggered.connect(lambda: QtWidgets.QMessageBox.aboutQt(self))
        self.licenseAction = QtGui.QAction("查看许可证")
        self.licenseAction.triggered.connect(self.showLinense)
        self.updatesAction = QtGui.QAction("更新内容")
        self.updatesAction.triggered.connect(self.showUpdates)
        self.openGithubAction = QtGui.QAction("Github")
        self.openGithubAction.triggered.connect(lambda: webbrowser.open_new_tab("https://www.github.com/hellojudger/hellojudger/"))
        self.aboutMenu.addActions([self.aboutHelloJudgerAction, self.aboutQtAction, self.licenseAction, self.updatesAction, self.openGithubAction])
        self.helpMenu.addMenu(self.aboutMenu)
        self.openExampleProblemAction = QtGui.QAction("打开示例")
        self.openExampleProblemAction.triggered.connect(self.openExampleProblem)
        self.openManualAction = QtGui.QAction("打开指南")
        self.openManualAction.triggered.connect(self.openManual)
        self.fileMenu.addActions([self.newProblemAction, self.openProblemAction])
        self.settingMenu.addActions([self.compileConfigureAction])
        self.fileMenu.addMenu(self.settingMenu)
        self.fileMenu.addActions([self.exitAction])
        self.editMenu.addActions([
            self.showAdditionalFileAction, self.editProblemStatementAction, self.editJudgingConfigureAction,
            self.editProblemConfigureAction
        ])
        self.helpMenu.addActions([self.openExampleProblemAction, self.openManualAction])
        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.helpMenu)
        self.editMenu.setDisabled(True)

    def openProblem(self, dialog=True, fp=""):
        if fp is None or fp.strip().rstrip() == "" or dialog:
            fp = QtWidgets.QFileDialog.getExistingDirectory(self, "打开题目文件夹")
            if fp is None or len(fp.strip().rstrip()) == 0:
                return
        if not os.path.isdir(os.path.join(fp, "testdata").replace("\\", "/")):
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "未找到测试点文件夹")
            return
        if not os.path.isfile(os.path.join(fp, "testdata/config.yaml").replace("\\", "/")):
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "未找到测试点配置文件")
            return
        global PROBLEM_PATH
        PROBLEM_PATH = fp
        self.contanier.setDisabled(False)
        self.editMenu.setDisabled(False)
        try:
            with open(os.path.join(fp, "problem_zh.md").replace("\\", "/"), encoding="utf-8") as f:
                md = f.read()
        except:
            md = "无法显示题面。"
        self.problem_shower.setValue(md)
        try:
            a = yaml.load(open(os.path.join(fp, "problem.yaml").replace("\\", "/"), "r", encoding="utf-8"),
                          Loader=yaml.FullLoader)
            self.setWindowTitle(a.get("title", "未知题目") + " - Hello Judger")
        except:
            self.setWindowTitle("未知题目 - Hello Judger")
        self.time_limit_shower.setText("<h3>" + get_time_limit() + "</h3>")

    def showAdditionalFile(self):
        global PROBLEM_PATH
        additional = os.path.join(PROBLEM_PATH, "additional_file").replace("\\", "/")
        if not os.path.isdir(additional):
            os.mkdir(additional)
        system_open_directry(additional)

    def editProblemStatement(self):
        global PROBLEM_PATH
        stat = os.path.join(PROBLEM_PATH, "problem_zh.md").replace("\\", "/")
        monaco.SimpleFileEidtorDialog("题面编辑器", stat)

    def editJudgingConfigure(self):
        global PROBLEM_PATH
        stat = os.path.join(PROBLEM_PATH, "testdata/config.yaml").replace("\\", "/")
        monaco.SimpleFileEidtorDialog("评测配置编辑器", stat)

    def editProblemConfigure(self):
        global PROBLEM_PATH
        stat = os.path.join(PROBLEM_PATH, "problem.yaml").replace("\\", "/")
        monaco.SimpleFileEidtorDialog("题目配置编辑器", stat)

    def openExampleProblem(self):
        examples = os.listdir("examples")
        choice = QtWidgets.QInputDialog.getItem(self, "Hello Judger", "选择您想打开的示例题目：", examples)
        if not choice[1]:
            return
        choice = choice[0]
        self.openProblem(False, os.path.join(os.path.abspath("examples/"), choice).replace("\\", "/"))

    def newProblem(self):
        dlg = ProblemCreator()
        dlg.create_done.connect(lambda x: self.openProblem(False, str(x)))
        dlg.exec()

    def judgeProblem_(self, code):
        dlg = ProblemJudgingDialog(
            self,
            self.language_choicer.currentText(),
            self.optimization_choicer.currentText(),
            code
        )
        dlg.exec()

    def judgingProblem(self):
        self.code_editor.getValue(self.judgeProblem_)

    def openManual(self):
        dlg = QtWidgets.QDialog(self)
        dlg.Layout = QtWidgets.QHBoxLayout()
        dlg.widget = QtWebEngineWidgets.QWebEngineView()
        dlg.widget.contextMenuEvent = lambda a0:a0.ignore()
        dlg.widget.load(QtCore.QUrl.fromLocalFile(os.path.abspath("resources/manual.html")))
        dlg.Layout.addWidget(dlg.widget)
        dlg.setLayout(dlg.Layout)
        dlg.setWindowTitle("Hello Judger 第三代用户文档")
        dlg.show()
        dlg.exec()
    
    def showLinense(self):
        dlg = QtWidgets.QDialog(self)
        dlg.Layout = QtWidgets.QVBoxLayout()
        dlg.widget = QTextBrowser()
        dlg.widget.setText(LICENSE)
        dlg.close_widget = QtWidgets.QPushButton("OK")
        dlg.close_widget.clicked.connect(lambda: dlg.close())
        dlg.Layout.addWidget(dlg.widget)
        dlg.Layout.addWidget(dlg.close_widget)
        dlg.setLayout(dlg.Layout)
        dlg.setWindowTitle("Hello Judger")
        dlg.show()
        dlg.exec()

    def showUpdates(self):
        dlg = QtWidgets.QDialog(self)
        dlg.Layout = QtWidgets.QVBoxLayout()
        dlg.widget = markdown_view.MarkdownView()
        dlg.widget.page().loadFinished.connect(lambda: dlg.widget.setValue(UPDATES))
        dlg.close_widget = QtWidgets.QPushButton("OK")
        dlg.close_widget.clicked.connect(lambda: dlg.close())
        dlg.Layout.addWidget(dlg.widget)
        dlg.Layout.addWidget(dlg.close_widget)
        dlg.setLayout(dlg.Layout)
        dlg.setWindowTitle("Hello Judger")
        dlg.show()
        dlg.exec()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    qtmodern.styles.light(app)
    win = HelloJudgerWindow()
    win.show()
    exit(app.exec())
