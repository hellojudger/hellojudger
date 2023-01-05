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
import accepting_chart
import oj_searcher
from zipfile import ZipFile

os.chdir(os.path.dirname(__file__))

compiler_settings = json.load(open("settings/compiler.json", "r", encoding="utf-8"))
PROBLEM_PATH = ""

with open("resources/ready.md", encoding="utf-8", mode="r") as f:
    ready_markdown = f.read()

with open("LICENSE", "r", encoding="utf-8") as f:
    LICENSE = f.read()

with open("resources/CHANGELOG.md", encoding="utf-8", mode="r") as f:
    UPDATES = f.read()

status_colorful = json.load(open("settings/status.colorful.json", "r"))

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
        def make_sta(sta):
            return QtWidgets.QLabel("<b style='color:rgb%s'>&nbsp;%s&nbsp;</b>" % (
                tuple(status_colorful.get(sta.replace(" ", ""), [21, 32, 102])), sta
            ))
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
            self.result_table.setCellWidget(pos, 1, make_sta(" %s " % args["sta"]))
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
        judge_finished = QtCore.pyqtSignal(bool, float)

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
                self.judge_finished.emit(total[0], total[1])

            except Exception as e:
                self.errored.emit(str(e))

            self.judge_done.emit()

    def judgeFinished(self, allac, total):
        global PROBLEM_PATH
        QApplication.processEvents()
        self.totalWidget.setText("总分：<b>%.2f</b>" % total)
        a = yaml.load(open(os.path.join(PROBLEM_PATH, "problem.yaml").replace("\\", "/"), "r", encoding="utf-8"),
            Loader=yaml.FullLoader)
        a = dict(a)
        if "nAccept" not in a.keys():
            a["nAccept"] = 0
        if "nSubmit" not in a.keys():
            a["nSubmit"] = 0
        a["nSubmit"] += 1
        if allac:
            a["nAccept"] += 1
        with open(os.path.join(PROBLEM_PATH, "problem.yaml").replace("\\", "/"), "w", encoding="utf-8") as f:
            yaml.dump(a, f)
        if allac:
            QtWidgets.QMessageBox.information(self, "Hello Judger", "评测完成！您通过了这道题，恭喜！")
        else:
            QtWidgets.QMessageBox.information(self, "Hello Judger", "评测完成！很遗憾，您没有通过本题！")

    def judgeDone(self):
        self.JUDGING = False

    def errored(self, e):
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
        self.submiter.header = QtWidgets.QLabel("<h1>提交代码</h1>")
        self.language_choicer = QtWidgets.QComboBox()
        self.language_choicer.addItems(list(map(lambda x: x["name"], compiler_settings.get("versions", []))))
        self.optimization_choicer = QtWidgets.QComboBox()
        self.optimization_choicer.addItems(list(map(lambda x: x["name"], compiler_settings.get("optimizations", []))))
        self.code_editor = monaco.MonacoEditor()
        self.submit_button = QtWidgets.QPushButton("提交")
        self.submit_button.clicked.connect(self.judgingProblem)
        self.submiter.Layout.addWidget(self.submiter.header)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>语言</b>"), self.language_choicer)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>优化</b>"), self.optimization_choicer)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>代码</b>"), self.code_editor)
        self.submiter.Layout.addWidget(self.submit_button)
        self.submiter.setLayout(self.submiter.Layout)
        self.metaView = QtWidgets.QWidget()
        self.metaView.Layout = QtWidgets.QFormLayout()
        self.problemNameLabel = QtWidgets.QLabel()
        self.tagsLabel = QtWidgets.QLabel()
        self.ownerLabel = QtWidgets.QLabel()
        self.time_limit_shower = QtWidgets.QLabel()
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>题目名</b>"), self.problemNameLabel)
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>标签</b>"), self.tagsLabel)
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>作者</b>"), self.ownerLabel)
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>时间限制</b>"), self.time_limit_shower)
        self.metaView.setLayout(self.metaView.Layout)
        self.rightCard = QtWidgets.QTabWidget()
        self.rightCard.addTab(self.submiter, "提交代码")
        self.rightCard.addTab(self.metaView, "附加信息")
        self.contanier.Layout.addWidget(self.problem_shower)
        self.contanier.Layout.addWidget(self.rightCard)
        self.contanier.Layout.setStretchFactor(self.problem_shower, 7)
        self.contanier.Layout.setStretchFactor(self.rightCard, 3)
        self.contanier.setLayout(self.contanier.Layout)
        self.contanier.setDisabled(True)
        self.setCentralWidget(self.contanier)
        self.setStyleSheet("*{font-family:微软雅黑,sans-serif;}")
        self.fileMenu = QtWidgets.QMenu("文件")
        self.openProblemAction = QtGui.QAction("打开题目")
        self.openProblemAction.triggered.connect(self.openProblem)
        self.newProblemAction = QtGui.QAction("新建题目")
        self.newProblemAction.triggered.connect(self.newProblem)
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
        self.toolMenu = QtWidgets.QMenu("工具")
        self.cleanCacheAction = QtGui.QAction("清理缓存")
        self.cleanCacheAction.triggered.connect(self.cleanCache)
        self.OJSearchAction = QtGui.QAction("OJ题面搜索")
        self.OJSearchAction.triggered.connect(self.OJSearch)
        self.loadFromHydroAction = QtGui.QAction("从Hydro导入")
        self.loadFromHydroAction.triggered.connect(self.loadFromHydro)
        self.settingMenu = QtWidgets.QMenu("设置")
        self.compileConfigureAction = QtGui.QAction("编译配置")
        self.compileConfigureAction.triggered.connect(lambda : monaco.SimpleFileEditorDialog("编译配置编辑器", "settings/compiler.json", self))
        self.colorfulStatusAction = QtGui.QAction("评测配色配置")
        self.colorfulStatusAction.triggered.connect(lambda : monaco.SimpleFileEditorDialog("评测配色配置编辑器", "settings/status.colorful.json", self))
        self.reopenProblemAction = QtGui.QAction("重新打开题目")
        self.reopenProblemAction.triggered.connect(lambda : self.openProblem(False, PROBLEM_PATH))
        self.helpMenu = QtWidgets.QMenu("帮助")
        self.aboutMenu = QtWidgets.QMenu("关于")
        self.aboutHelloJudgerAction = QtGui.QAction("关于本程序")
        self.aboutHelloJudgerAction.triggered.connect(lambda: QtWidgets.QMessageBox.information(self,
            "关于 Hello Judger",
            "Hello Judger 第三代 1.2 by xiezheyuan."
        ))
        self.aboutQtAction = QtGui.QAction("关于 Qt")
        self.aboutQtAction.triggered.connect(lambda: QtWidgets.QMessageBox.aboutQt(self, "Hello Judger"))
        self.licenseAction = QtGui.QAction("查看许可证")
        self.licenseAction.triggered.connect(self.showLinense)
        self.updatesAction = QtGui.QAction("更新内容")
        self.updatesAction.triggered.connect(self.showUpdates)
        self.openGithubAction = QtGui.QAction("Github")
        self.openGithubAction.triggered.connect(lambda: webbrowser.open_new_tab("https://www.github.com/hellojudger/hellojudger/"))
        self.aboutMenu.addActions([self.aboutHelloJudgerAction, self.aboutQtAction, self.licenseAction, self.updatesAction, self.openGithubAction])
        self.helpMenu.addMenu(self.aboutMenu)
        self.openExampleProblemAction = QtGui.QAction("打开示例题目")
        self.openExampleProblemAction.triggered.connect(self.openExampleProblem)
        self.openManualAction = QtGui.QAction("打开文档")
        self.openManualAction.triggered.connect(self.openManual)
        self.fileMenu.addActions([
            self.newProblemAction, self.openProblemAction, self.reopenProblemAction,
            self.exitAction
        ])
        self.editMenu.addActions([
            self.showAdditionalFileAction, self.editProblemStatementAction, self.editJudgingConfigureAction,
            self.editProblemConfigureAction
        ])
        self.toolMenu.addActions([
            self.cleanCacheAction, self.OJSearchAction,
            self.loadFromHydroAction
        ])
        self.settingMenu.addActions([self.compileConfigureAction, self.colorfulStatusAction])
        self.helpMenu.addActions([
            self.openExampleProblemAction, self.openManualAction
        ])
        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.toolMenu)
        self.menuBar().addMenu(self.settingMenu)
        self.menuBar().addMenu(self.helpMenu)
        self.editMenu.setDisabled(True)
        self.reopenProblemAction.setDisabled(True)
        self.setWindowIcon(QtGui.QIcon("resources/icon.png"))
        self.OJSearchAction.setDisabled(True)

    CHART_TAB = 0

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
        self.reopenProblemAction.setDisabled(False)
        self.OJSearchAction.setDisabled(False)
        try:
            with open(os.path.join(fp, "problem_zh.md").replace("\\", "/"), encoding="utf-8") as f:
                md = f.read()
        except:
            md = "无法显示题面。"
        self.problem_shower.setValue(md)
        try:
            a = yaml.load(open(os.path.join(fp, "problem.yaml").replace("\\", "/"), "r", encoding="utf-8"),
                          Loader=yaml.FullLoader)
            self.setWindowTitle(str(a.get("title", "未知题目")) + " - Hello Judger")
            self.problemNameLabel.setText(str(a.get("title", "未知题目")))
            self.tagsLabel.setText(", ".join(list(map(str, a.get("tag", ["没有设置标签"])))))
            self.ownerLabel.setText(str(a.get("owner", "匿名")))
            if not (a.get("nAccept", 0) == 0 and a.get("nSubmit", 0) == 0):
                if self.CHART_TAB != 0:
                    self.rightCard.removeTab(self.CHART_TAB)
                chart = accepting_chart.AcceptingChart(int(a.get("nSubmit")), int(a.get("nAccept")))
                self.rightCard.addTab(chart, "通过量统计")
                self.CHART_TAB = self.rightCard.count() - 1
            else:
                self.CHART_TAB = 0
        except:
            self.setWindowTitle("未知题目 - Hello Judger")
            self.setWindowTitle("未知题目" + " - Hello Judger")
            self.problemNameLabel.setText("未知题目")
            self.tagsLabel.setText("没有设置标签")
            self.ownerLabel.setText("匿名")
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
        monaco.SimpleFileEditorDialog("题面编辑器", stat, self)

    def editJudgingConfigure(self):
        global PROBLEM_PATH
        stat = os.path.join(PROBLEM_PATH, "testdata/config.yaml").replace("\\", "/")
        monaco.SimpleFileEditorDialog("评测配置编辑器", stat, self)

    def editProblemConfigure(self):
        global PROBLEM_PATH
        stat = os.path.join(PROBLEM_PATH, "problem.yaml").replace("\\", "/")
        monaco.SimpleFileEditorDialog("题目配置编辑器", stat, self)

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
        dlg.Layout = QtWidgets.QVBoxLayout()
        dlg.widget = QtWebEngineWidgets.QWebEngineView()
        dlg.widget.contextMenuEvent = lambda a0:a0.ignore()
        dlg.widget.load(QtCore.QUrl.fromLocalFile(os.path.abspath("resources/manual.html")))
        dlg.Layout.addWidget(dlg.widget)
        dlg.close_widget = QtWidgets.QPushButton("OK")
        dlg.close_widget.clicked.connect(lambda: dlg.close())
        dlg.Layout.addWidget(dlg.close_widget)
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

    def cleanCache(self):
        need_remove = []
        if os.path.isdir(os.path.abspath("compiling")):
            for i in os.listdir(os.path.abspath("compiling")):
                fn = os.path.join(os.path.abspath("compiling"), i)
                if os.path.isfile(fn):
                    need_remove.append(fn)
        if os.path.isdir(os.path.abspath("checking")):
            for i in os.listdir(os.path.abspath("checking")):
                fn = os.path.join(os.path.abspath("checking"), i)
                if os.path.isfile(fn):
                    need_remove.append(fn)
        if os.path.isfile(os.path.abspath("report.xml")):
            need_remove.append("report.xml")
        dlg = QtWidgets.QProgressDialog("正在清理", "取消", 0, len(need_remove), parent=self)
        dlg.open()
        dlg.setWindowTitle("Hello Judger")
        cleaned = 0
        for i in range(1, len(need_remove)+1):
            if dlg.wasCanceled():
                dlg.close()
                QtWidgets.QMessageBox.critical(self, "Hello Judger", "操作被用户取消")
                return
            try:
                os.remove(need_remove[i-1])
            except:
                pass
            else:
                cleaned += 1
            QApplication.processEvents()
            dlg.setValue(i)
        if os.path.isdir("checking") and len(os.listdir(os.path.abspath("checking"))) == 0:
            os.rmdir("checking")
        if os.path.isdir("compiling") and len(os.listdir(os.path.abspath("compiling"))) == 0:
            os.rmdir("compiling")
        dlg.close()
        QtWidgets.QMessageBox.information(self, "Hello Judger", "清理完成！共清理 %d 个缓存文件。" % (cleaned))

    def OJSearch(self):
        global PROBLEM_PATH
        try:
            with open(os.path.join(PROBLEM_PATH, "problem_zh.md").replace("\\", "/"), encoding="utf-8") as f:
                md = f.read()
        except:
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "未找到题面。")
            return
        oj_searcher.OJSearcherDialog(md, self)

    def loadFromHydro(self):
        uuid = str(__import__("uuid").uuid4())
        QtWidgets.QMessageBox.information(self, "Hello Judger", "下面将进入 Hydro 题目压缩包导入。\n由于 Hello Judger 的设计参考了 Hydro，因此您可以方便地导入，但是对于某些特殊的地方需要您手动更改\n您选定的目录下会生成一个数字文件夹，那才是真正的题目文件夹。")
        zipfile = QtWidgets.QFileDialog.getOpenFileName(self, "选择 Hydro 题目压缩包 - Hello Judger", 
            initialFilter="Hydro 题目压缩包文件 (*.zip)")[0]
        if zipfile.strip().rstrip() == "":
            return
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选择保存目录 - Hello Judger")
        if directory.strip().rstrip() == "":
            return
        fobj = ZipFile(zipfile)
        dlg = QtWidgets.QProgressDialog("正在解压缩……", "取消", 0, len(fobj.namelist()))
        dlg.setWindowTitle("Hello Judger")
        dlg.open()
        folder = ""
        for i in fobj.namelist():
            folder = i.split('/')[0]
            if dlg.wasCanceled():
                QtWidgets.QMessageBox.critical(self, "Hello Judger", "操作被用户取消。")
                return
            fobj.extract(i, directory)
            dlg.setValue(dlg.value() + 1)
            QApplication.processEvents()
        dlg.setValue(len(fobj.namelist()))
        dlg.close()
        QtWidgets.QMessageBox.information(self, "Hello Judger", "操作完成！")
        self.openProblem(False, os.path.join(directory,folder).replace("\\", "/"))

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    qtmodern.styles.light(app)
    win = HelloJudgerWindow()
    win.show()
    exit(app.exec())
