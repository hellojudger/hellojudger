import os
import sys
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
import webbrowser
import oj_searcher
from zipfile import ZipFile
import settings_dialog
import qtawesome
import qdarktheme
import darkdetect

compiler_settings = json.load(open("settings/compiler.json", "r", encoding="utf-8"))
PROBLEM_PATH = ""

with open("resources/ready.md", encoding="utf-8", mode="r") as f:
    ready_markdown = f.read()

with open("resources/license.md", "r", encoding="utf-8") as f:
    LICENSE = f.read()

with open("resources/CHANGELOG.md", encoding="utf-8", mode="r") as f:
    UPDATES = f.read()

status_colorful = json.load(open("settings/status.colorful.json", "r", encoding="utf-8"))
status_chinese = json.load(open("settings/status.chinese.json", "r", encoding="utf-8"))
ui_theme_json = json.load(open("settings/ui_theme.json", "r", encoding="utf-8"))
theme = ui_theme_json.get("theme", "dark")

if theme == "auto":
    if darkdetect.isLight():
        theme = "light"
    else:
        theme = "dark"

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

def restart():
    # https://www.jiang-cheng.com/collection-of-works/seo-tools-collection-of-works/926.html
    python = sys.executable
    if platform.system().lower() == 'windows':
        os.execl(python, "%s", * sys.argv)%(python)
    else:
        os.execl(python, python, * sys.argv)


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
            file = QtWidgets.QFileDialog.getOpenFileName(None, "????????????", dire)
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
            file = QtWidgets.QFileDialog.getExistingDirectory(None, "????????????", dire)
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
        self.problemNameInputer = QtWidgets.QLineEdit("??????????????????")
        self.timeLimitInputer = QtWidgets.QSpinBox()
        self.timeLimitInputer.setMinimum(0)
        self.timeLimitInputer.setMaximum(60000)
        self.timeLimitInputer.setValue(1000)
        self.exportInputer = DirectoryEdit()
        self.do = QtWidgets.QPushButton("????????????(F11)")
        self.do.setShortcut("F11")
        self.do.clicked.connect(self.create_pro)
        self.Layout.addWidget(QtWidgets.QLabel("<h2>??????????????????</h2>"))
        self.Layout.addRow(QtWidgets.QLabel("<b>?????????</b>"), self.problemNameInputer)
        self.Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), self.statementInputer)
        self.Layout.addRow(QtWidgets.QLabel("<b>???????????????</b>"), self.testdataInputer)
        self.Layout.addRow(QtWidgets.QLabel("<b>????????????(??????:??????)</b>"), self.timeLimitInputer)
        self.Layout.addRow(QtWidgets.QLabel("<b>????????????</b>"), self.exportInputer)
        self.Layout.addWidget(self.do)
        self.setLayout(self.Layout)
        self.setStyleSheet("*{font-family:SimHei,sans;}")
        self.setWindowTitle("Hello Judger ??????????????????")

    def create_pro(self):
        all_ = 5 + len(os.listdir(self.testdataInputer.value()))
        dlg = QtWidgets.QProgressDialog("??????????????????", "??????", 0, all_, self)
        dlg.setWindowTitle("???????????? - Hello Judger")
        dlg.open()
        value = 0
        joiner = lambda y: os.path.join(self.exportInputer.value(), y).replace("\\", "/")
        try:
            shutil.copyfile(self.statementInputer.value(), joiner("problem_zh.md"))
            value = value + 1
            dlg.setValue(value)
            QApplication.processEvents()
            with open(joiner("problem.yaml"), "w", encoding="utf-8") as f:
                f.write("title: %s\n" % repr(str(self.problemNameInputer.text())))
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
                    raise Exception("?????????????????????")
                name = os.path.join(self.testdataInputer.value(), i).replace("\\", "/")
                value = value + 1
                dlg.setValue(value)
                if not os.path.isfile(name):
                    continue
                shutil.copyfile(name, joiner("testdata/%s" % i))
        except Exception as err:
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "?????????????????????:\n" + str(err))
            dlg.close()
            return
        dlg.setValue(all_)
        QtWidgets.QMessageBox.information(self, "Hello Judger", "???????????????")
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
        self.start_btn = QtWidgets.QPushButton("??????(F11)")
        self.start_btn.setShortcut("F11")
        self.start_btn.clicked.connect(self.startJudge)
        self.bottom_card = QtWidgets.QWidget()
        self.bottom_card.Layout = QtWidgets.QHBoxLayout()
        self.logging = QTextBrowser()
        self.logging.append("??????????????????????????????\n")
        self.result_table = QtWidgets.QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["???????????????", "??????", "??????", "??????"])
        self.bottom_card.Layout.addWidget(self.result_table)
        self.bottom_card.Layout.addWidget(self.logging)
        self.bottom_card.setLayout(self.bottom_card.Layout)
        self.totalWidget = QtWidgets.QLabel()
        self.Layout.addWidget(self.start_btn)
        self.Layout.addWidget(self.bottom_card)
        self.Layout.addWidget(self.totalWidget)
        self.setLayout(self.Layout)
        self.setFixedSize(800, 400)
        self.setWindowTitle("???????????? - Hello Judger")

    MESSAGES = ""

    def append(self, txt):
        QApplication.processEvents()
        txt = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "] " + txt
        self.logging.append(txt)
        self.MESSAGES = self.MESSAGES + txt + "\n"

    TABLE = []

    def slot(self, type, args):
        def make_sta(sta, msg):
            if status_chinese.get("enabled", False):
                sta_ = status_chinese.get("content", {}).get(sta.replace(" ", ""), sta)
            else:
                sta_ = sta
            lbl = QtWidgets.QLabel("<b style='color:rgb%s'>&nbsp;%s&nbsp;</b>" % (
                tuple(status_colorful.get(sta.replace(" ", ""), [21, 32, 102])), sta_
            ))
            def event(a0):
                QtWidgets.QMessageBox.information(self, "Hello Judger", msg)
                a0.accept()
            lbl.mouseDoubleClickEvent = event
            return lbl
        QApplication.processEvents()
        if type == "judge_begin":
            self.append("????????????")
        elif type == "testlib_compile_begin":
            self.append("Testlib Checker ????????????")
        elif type == "testlib_compile_error":
            QtWidgets.QMessageBox.cirtical(self, "Hello Judger", "Testlib Checker ????????????")
        elif type == "testlib_compile_finished":
            self.append("Testlib Checker ????????????")
        elif type == "scan_begin":
            self.append("??????????????????????????????")
        elif type == "scan_find_task":
            self.append("????????? ?????????%s ?????????%s" % (args["input"], args["output"]))
        elif type == "scan_finished":
            self.append("????????????????????????")
        elif type == "cases_begin":
            self.append("Cases ????????????")
        elif type == "task_begin":
            self.append("????????? %s/%s ????????????" % (args["input"], args["output"]))
        elif type == "task_finished":
            self.TABLE.append(args)
            self.append("????????? %s/%s ????????????,????????? %s,????????? %.2f,?????? %.4fs,????????? %s" % (
                args["input"], args["output"], args["sta"], args["pts"], args["time"], args["msg"]))
            self.result_table.setRowCount(self.result_table.rowCount() + 1)
            pos = self.result_table.rowCount() - 1
            self.result_table.setCellWidget(pos, 0, QtWidgets.QLabel(" %s " % (args["input"].rsplit('.', 1)[0])))
            self.result_table.setCellWidget(pos, 1, make_sta("%s" % args["sta"], args["msg"]))
            self.result_table.setCellWidget(pos, 2, QtWidgets.QLabel(" %.2f " % args["pts"]))
            self.result_table.setCellWidget(pos, 3, QtWidgets.QLabel(" %.2fs " % args["time"]))
            self.result_table.resizeColumnsToContents()
        elif type == "subtasks_begin":
            self.append("Subtasks ????????????")
        elif type == "subtask_begin":
            self.append("Subtask #%s ??????" % str(args["id"]))
        elif type == "subtask_ignored":
            self.append("??? Subtask ?????????")
        elif type == "subtask_finished":
            self.append("Subtask #%s ??????,?????? %.2f" % (str(args["id"]), args["total"]))
        elif type == "subtasks_finished":
            self.append("Subtasks ????????????")
        elif type == "judge_finished":
            self.append("????????????")

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
        if allac is None:
            return
        global PROBLEM_PATH
        QApplication.processEvents()
        self.totalWidget.setText("?????????<b>%.2f</b>" % total)
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
            msg = "???????????????????????????????????????????????? %.2f ???????????????" % total
        else:
            msg = "??????????????????????????????????????? %.2f ??????????????????????????????" % total
        if os.path.isfile(os.path.join(PROBLEM_PATH, "submissions.json")):
            submissions = json.load(open(os.path.join(PROBLEM_PATH, "submissions.json"), "r", encoding="utf-8"))
        else:
            submissions = []
        submissions.append({"code" : self.code, "version" : self.version, "optimization" : self.optimization,
            "total" : total, "time" : __import__("time").time(), "computer_name" : __import__("socket").gethostname(),
            "user_name" : __import__("getpass").getuser(), "isAccepted" : allac, "judgingInfo" : self.TABLE, "logging" : self.MESSAGES})
        json.dump(submissions, open(os.path.join(PROBLEM_PATH, "submissions.json"), "w", encoding="utf-8"))
        QtWidgets.QMessageBox.information(self, "Hello Judger", msg)

    def judgeDone(self):
        self.JUDGING = False

    def errored(self, e):
        QtWidgets.QMessageBox.critical(self, "Hello Judger", "????????????????????????\n" + str(e))

    def startJudge(self):
        self.TABLE = []
        self.MESSAGES = ""
        self.JUDGING = True
        self.result_table.clearContents()
        self.result_table.setRowCount(0)
        self.logging.clear()
        QApplication.processEvents()
        self.append("????????????")
        QApplication.processEvents()
        try:
            prog = compile.compile_cpp(self.code, self.version, self.optimization)
        except:
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "????????????")
            self.JUDGING = False
            return
        self.append("????????????")
        QApplication.processEvents()
        thread = self.JudgingThread(self)
        thread.judge_done.connect(self.judgeDone)
        thread.judge_finished.connect(self.judgeFinished)
        thread.message.connect(self.slot)
        thread.errored.connect(self.errored)
        thread.run(prog)


class QAction(QtGui.QAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SubmissionDetailsDialog(QtWidgets.QDialog):
    def __init__(self, obj:dict, parent=None):
        def make_sta(sta):
            lbl = QtWidgets.QLabel("<b style='color:rgb%s'>&nbsp;%s&nbsp;</b>" % (
                tuple(status_colorful.get(sta.replace(" ", ""), [21, 32, 102])), sta
            ))
            return lbl
        def make_sta2(sta, msg):
            if status_chinese.get("enabled", False):
                sta_ = status_chinese.get("content", {}).get(sta.replace(" ", ""), sta)
            else:
                sta_ = sta
            lbl = QtWidgets.QLabel("<b style='color:rgb%s'>&nbsp;%s&nbsp;</b>" % (
                tuple(status_colorful.get(sta.replace(" ", ""), [21, 32, 102])), sta_
            ))
            def event(a0):
                QtWidgets.QMessageBox.information(self, "Hello Judger", msg)
                a0.accept()
            lbl.mouseDoubleClickEvent = event
            return lbl
        super().__init__(parent=parent)
        ALLLAYOUT = QtWidgets.QVBoxLayout()
        ALLTAB = QtWidgets.QTabWidget()
        FIRSTTAB = QtWidgets.QFrame()
        Layout = QtWidgets.QFormLayout()
        Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), QtWidgets.QLabel(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(obj.get("time", 0)))))
        Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), QtWidgets.QLabel(" %.2f " % obj.get("total", 0)))
        if obj.get("isAccepted", False):
            Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), make_sta("Accepted"))
        else:
            Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), make_sta("Unaccepted"))
        Layout.addRow(QtWidgets.QLabel("<b>"))
        Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), QtWidgets.QLabel(obj.get("version", "N/A")))
        Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), QtWidgets.QLabel(obj.get("optimization", "N/A")))
        Layout.addRow(QtWidgets.QLabel("<b>??????????????????</b>"), QtWidgets.QLabel(obj.get("computer_name", "N/A")))
        Layout.addRow(QtWidgets.QLabel("<b>???????????????</b>"), QtWidgets.QLabel(obj.get("user_name", "N/A")))
        FIRSTTAB.setLayout(Layout)
        ALLTAB.addTab(FIRSTTAB, "????????????")
        monaco_ = monaco.MonacoEditor()
        def _():
            monaco_.page().runJavaScript(r"editor.updateOptions({readOnly: true});")
            monaco_.setValue(obj.get("code", ""))
        monaco_.page().loadFinished.connect(_)
        ALLTAB.addTab(monaco_, "??????")
        result_table = QtWidgets.QTableWidget()
        result_table.setColumnCount(4)
        result_table.setHorizontalHeaderLabels(["???????????????", "??????", "??????", "??????"])
        for args in obj.get("judgingInfo", []):
            result_table.setRowCount(result_table.rowCount() + 1)
            pos = result_table.rowCount() - 1
            result_table.setCellWidget(pos, 0, QtWidgets.QLabel(" %s " % (args["input"].rsplit('.', 1)[0])))
            result_table.setCellWidget(pos, 1, make_sta2("%s" % args["sta"], args["msg"]))
            result_table.setCellWidget(pos, 2, QtWidgets.QLabel(" %.2f " % args["pts"]))
            result_table.setCellWidget(pos, 3, QtWidgets.QLabel(" %.2fs " % args["time"]))
            result_table.resizeColumnsToContents()
        ALLTAB.addTab(result_table, "???????????????")
        logging_browser = QTextBrowser()
        logging_browser.setText(obj.get("logging", ""))
        ALLTAB.addTab(logging_browser, "????????????")
        ALLLAYOUT.addWidget(ALLTAB)
        exitbutton = QtWidgets.QPushButton("OK")
        exitbutton.clicked.connect(self.close)
        ALLLAYOUT.addWidget(exitbutton)
        self.setLayout(ALLLAYOUT)
        self.setWindowTitle("???????????????????????? - Hello Judger")
        self.show()
        self.exec()


class HelloJudgerWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Hello Judger")
        self.contanier = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.problem_shower = markdown_view.MarkdownView()
        self.problem_shower.page().loadFinished.connect(lambda: self.problem_shower.setValue(ready_markdown))
        self.submiter = QtWidgets.QWidget()
        self.submiter.Layout = QtWidgets.QFormLayout()
        self.submiter.header = QtWidgets.QLabel("<h1>????????????</h1>")
        self.language_choicer = QtWidgets.QComboBox()
        self.language_choicer.addItems(list(map(lambda x: x["name"], compiler_settings.get("versions", []))))
        self.optimization_choicer = QtWidgets.QComboBox()
        self.optimization_choicer.addItems(list(map(lambda x: x["name"], compiler_settings.get("optimizations", []))))
        self.code_editor = monaco.MonacoEditor()
        self.submit_button = QtWidgets.QPushButton(qtawesome.icon("fa.paper-plane"),"??????(F11)")
        self.submit_button.setShortcut("F11")
        self.submit_button.clicked.connect(self.judgingProblem)
        self.independentEditorButton = QtWidgets.QPushButton(qtawesome.icon("mdi.resize"), "??????????????????(Ctrl+Alt+E)")
        self.independentEditorButton.setShortcut("Ctrl+Alt+E")
        self.independentEditorButton.clicked.connect(self.independentEditor)
        self.submiter.Layout.addWidget(self.submiter.header)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), self.language_choicer)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), self.optimization_choicer)
        self.submiter.Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), self.code_editor)
        self.submiter.Layout.addWidget(self.submit_button)
        self.submiter.Layout.addWidget(self.independentEditorButton)
        self.submiter.setLayout(self.submiter.Layout)
        self.metaView = QtWidgets.QWidget()
        self.metaView.Layout = QtWidgets.QFormLayout()
        self.problemNameLabel = QtWidgets.QLabel()
        self.tagsLabel = QtWidgets.QLabel()
        self.ownerLabel = QtWidgets.QLabel()
        self.time_limit_shower = QtWidgets.QLabel()
        self.submitCountLabel = QtWidgets.QLabel()
        self.acceptedCountLabel = QtWidgets.QLabel()
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>?????????</b>"), self.problemNameLabel)
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), self.tagsLabel)
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>??????</b>"), self.ownerLabel)
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>????????????</b>"), self.time_limit_shower)
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>????????????</b>"), self.submitCountLabel)
        self.metaView.Layout.addRow(QtWidgets.QLabel("<b>????????????</b>"), self.acceptedCountLabel)
        self.metaView.setLayout(self.metaView.Layout)
        self.submissionsView = QtWidgets.QTableWidget()
        self.rightCard = QtWidgets.QTabWidget()
        self.rightCard.addTab(self.submiter, "????????????")
        self.rightCard.addTab(self.metaView, "????????????")
        self.rightCard.addTab(self.submissionsView, "????????????")
        self.contanier.addWidget(self.problem_shower)
        self.contanier.addWidget(self.rightCard)
        self.contanier.setStretchFactor(0, 7)
        self.contanier.setStretchFactor(1, 3)
        self.rightCard.setDisabled(True)
        self.setCentralWidget(self.contanier)
        self.fileMenu = QtWidgets.QMenu("??????(&F)")
        self.openProblemAction = QAction(qtawesome.icon("ei.folder-open"), "????????????(&O)")
        self.openProblemAction.setShortcut(QtGui.QKeySequence.StandardKey.Open)
        self.openProblemAction.triggered.connect(self.openProblem)
        self.newProblemAction = QAction(qtawesome.icon("ei.file-new"), "????????????(&N)")
        self.newProblemAction.setShortcut(QtGui.QKeySequence.StandardKey.New)
        self.newProblemAction.triggered.connect(self.newProblem)
        self.exitAction = QAction(qtawesome.icon("mdi.exit-to-app"), "????????????(&X)")
        self.exitAction.triggered.connect(exit)
        self.restartAction = QAction(qtawesome.icon("msc.debug-restart"), "????????????(&R)")
        self.restartAction.triggered.connect(restart)
        self.restartAction.setShortcut(QtGui.QKeySequence.StandardKey.Refresh)
        self.editMenu = QtWidgets.QMenu("??????(&E)")
        self.showAdditionalFileAction = QAction(qtawesome.icon("ri.file-add-fill"), "????????????(&A)")
        self.showAdditionalFileAction.triggered.connect(self.showAdditionalFile)
        self.editProblemStatementAction = QAction(qtawesome.icon("mdi.file-document-outline"), "??????(&S)")
        self.editProblemStatementAction.triggered.connect(self.editProblemStatement)
        self.editJudgingConfigureAction = QAction(qtawesome.icon("msc.settings-gear"), "????????????(&J)")
        self.editJudgingConfigureAction.triggered.connect(self.editJudgingConfigure)
        self.editProblemConfigureAction = QAction(qtawesome.icon("msc.settings-gear"), "????????????(&P)")
        self.editProblemConfigureAction.triggered.connect(self.editProblemConfigure)
        self.toolMenu = QtWidgets.QMenu("??????(&T)")
        self.cleanCacheAction = QAction(qtawesome.icon("fa.recycle"), "????????????(&C)")
        self.cleanCacheAction.triggered.connect(self.cleanCache)
        self.cleanCacheAction.setShortcut("Ctrl+Shift+Delete")
        self.OJSearchAction = QAction(qtawesome.icon("fa.search"), "OJ????????????(&S)")
        self.OJSearchAction.setShortcut("Ctrl+Shift+F1")
        self.OJSearchAction.triggered.connect(self.OJSearch)
        self.loadFromHydroAction = QAction(qtawesome.icon("mdi.database-import-outline"), "???&Hydro??????")
        self.loadFromHydroAction.triggered.connect(self.loadFromHydro)
        self.settingMenu = QtWidgets.QMenu("??????(&P)")
        self.compileConfigureAction = QAction(qtawesome.icon("msc.settings"), "????????????(&C)")
        self.compileConfigureAction.triggered.connect(lambda : monaco.SimpleFileEditorDialog("?????????????????????", "settings/compiler.json", self))
        self.colorfulStatusAction = QAction(qtawesome.icon("msc.symbol-color"), "??????????????????(&J)")
        self.colorfulStatusAction.triggered.connect(lambda : settings_dialog.StatusColorfulDialog(self))
        self.chineseStatusAction = QAction(qtawesome.icon("fa.language"), "??????????????????(&Z)")
        self.chineseStatusAction.triggered.connect(lambda : settings_dialog.StatusChineseDialog(self))
        self.uiSettingAction = QAction(qtawesome.icon("mdi.theme-light-dark"), "??????????????????(&T)")
        self.uiSettingAction.triggered.connect(lambda : settings_dialog.UiThemeDialog(self))
        self.uiSettingAction.setShortcut("Ctrl+Shift+T")
        self.helpMenu = QtWidgets.QMenu("??????(&H)")
        self.aboutMenu = QtWidgets.QMenu("??????(&I)")
        self.aboutHelloJudgerAction = QAction(qtawesome.icon("ei.info-circle"), "???????????????(&P)")
        self.aboutHelloJudgerAction.triggered.connect(lambda: QtWidgets.QMessageBox.information(self,
            "?????? Hello Judger",
            "Hello Judger ????????? 1.5 by xiezheyuan."
        ))
        self.aboutQtAction = QAction(qtawesome.icon("mdi.information-outline"), "?????? &Qt")
        self.aboutQtAction.triggered.connect(lambda: QtWidgets.QMessageBox.aboutQt(self, "Hello Judger"))
        self.licenseAction = QAction(qtawesome.icon("mdi.license"), "???????????????(&L)")
        self.licenseAction.triggered.connect(self.showLinense)
        
        self.updatesAction = QAction(qtawesome.icon("mdi.update"), "????????????(&U)")
        self.updatesAction.triggered.connect(self.showUpdates)
        self.openGithubAction = QAction(qtawesome.icon("fa.github"), "&Github")
        self.openGithubAction.triggered.connect(lambda: webbrowser.open_new_tab("https://www.github.com/hellojudger/hellojudger/"))
        self.aboutMenu.addActions([self.aboutHelloJudgerAction, self.aboutQtAction, self.licenseAction, self.updatesAction, self.openGithubAction])
        self.helpMenu.addMenu(self.aboutMenu)
        self.openExampleProblemAction = QAction(qtawesome.icon("fa5s.book-open"), "??????????????????(&X)")
        self.openExampleProblemAction.triggered.connect(self.openExampleProblem)
        self.openExampleProblemAction.setShortcut("Ctrl+Alt+X")
        self.openManualAction = QAction(qtawesome.icon("mdi.help-circle-outline"), "????????????(&D)")
        self.openManualAction.triggered.connect(self.openManual)
        self.openManualAction.setShortcut("Ctrl+Alt+D")
        self.fileMenu.addActions([
            self.newProblemAction, self.openProblemAction,
            self.exitAction, self.restartAction
        ])
        self.editMenu.addActions([
            self.showAdditionalFileAction, self.editProblemStatementAction, self.editJudgingConfigureAction,
            self.editProblemConfigureAction
        ])
        self.toolMenu.addActions([
            self.cleanCacheAction, self.OJSearchAction,
            self.loadFromHydroAction
        ])
        self.settingMenu.addActions([
            self.compileConfigureAction, self.colorfulStatusAction,
            self.chineseStatusAction, self.uiSettingAction
        ])
        self.helpMenu.addActions([
            self.openExampleProblemAction, self.openManualAction
        ])
        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.toolMenu)
        self.menuBar().addMenu(self.settingMenu)
        self.menuBar().addMenu(self.helpMenu)
        self.editMenu.setDisabled(True)
        self.setWindowIcon(qtawesome.icon("ph.circle-wavy-check-fill", color='gold'))
        self.OJSearchAction.setDisabled(True)

    CHART_TAB = 0

    def openProblem(self, dialog=True, fp=""):
        if fp is None or fp.strip().rstrip() == "" or dialog:
            fp = QtWidgets.QFileDialog.getExistingDirectory(self, "?????????????????????")
            if fp is None or len(fp.strip().rstrip()) == 0:
                return
        if not os.path.isdir(os.path.join(fp, "testdata").replace("\\", "/")):
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "???????????????????????????")
            return
        if not os.path.isfile(os.path.join(fp, "testdata/config.yaml").replace("\\", "/")):
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "??????????????????????????????")
            return
        global PROBLEM_PATH
        PROBLEM_PATH = fp
        self.rightCard.setDisabled(False)
        self.editMenu.setDisabled(False)
        self.OJSearchAction.setDisabled(False)
        try:
            with open(os.path.join(fp, "problem_zh.md").replace("\\", "/"), encoding="utf-8") as f:
                md = f.read()
        except:
            md = "?????????????????????"
        self.problem_shower.setValue(md)
        try:
            a = yaml.load(open(os.path.join(fp, "problem.yaml").replace("\\", "/"), "r", encoding="utf-8"),
                          Loader=yaml.FullLoader)
            self.setWindowTitle(str(a.get("title", "????????????")) + " - Hello Judger")
            self.problemNameLabel.setText(str(a.get("title", "????????????")))
            self.tagsLabel.setText(", ".join(list(map(str, a.get("tag", ["??????????????????"])))))
            self.ownerLabel.setText(str(a.get("owner", "??????")))
            self.submitCountLabel.setText(str(a.get("nSubmit", 0)))
            self.acceptedCountLabel.setText(str(a.get("nAccept", 0)))
        except:
            self.setWindowTitle("???????????? - Hello Judger")
            self.setWindowTitle("????????????" + " - Hello Judger")
            self.problemNameLabel.setText("????????????")
            self.tagsLabel.setText("??????????????????")
            self.ownerLabel.setText("??????")
            self.submitCountLabel.setText(str(0))
            self.acceptedCountLabel.setText(str(0))
        self.time_limit_shower.setText("<h3>" + get_time_limit() + "</h3>")
        def make_sta(sta):
            lbl = QtWidgets.QLabel("<b style='color:rgb%s'>&nbsp;%s&nbsp;</b>" % (
                tuple(status_colorful.get(sta.replace(" ", ""), [21, 32, 102])), sta
            ))
            return lbl
        if os.path.isfile(os.path.join(PROBLEM_PATH, "submissions.json")):
            self.submissionsView.clear()
            self.submissionsView.setColumnCount(4)
            self.submissionsView.setHorizontalHeaderLabels(["??????", "??????", "??????", "????????????"])
            data = json.load(open(os.path.join(PROBLEM_PATH, "submissions.json"), "r", encoding="utf-8"))
            buttons = []
            for i in data:
                self.submissionsView.setRowCount(self.submissionsView.rowCount() + 1)
                self.submissionsView.setCellWidget(self.submissionsView.rowCount()-1, 0, 
                    QtWidgets.QLabel(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i.get("time", 0)))))
                self.submissionsView.setCellWidget(self.submissionsView.rowCount()-1, 1, QtWidgets.QLabel(" %.2f " % i.get("total", 0)))
                if i.get("isAccepted", False):
                    self.submissionsView.setCellWidget(self.submissionsView.rowCount()-1, 2, make_sta("Accepted"))
                else:
                    self.submissionsView.setCellWidget(self.submissionsView.rowCount()-1, 2, make_sta("Unaccepted"))
                button = QtWidgets.QPushButton("...")
                def _(obj):
                    def __():
                        SubmissionDetailsDialog(obj, self)
                    return __
                button.clicked.connect(_(i))
                buttons.append(button)
                self.submissionsView.setCellWidget(self.submissionsView.rowCount()-1, 3, buttons[len(buttons)-1])
            self.submissionsView.resizeColumnsToContents()

    def showAdditionalFile(self):
        global PROBLEM_PATH
        additional = os.path.join(PROBLEM_PATH, "additional_file").replace("\\", "/")
        if not os.path.isdir(additional):
            os.mkdir(additional)
        system_open_directry(additional)

    def editProblemStatement(self):
        global PROBLEM_PATH
        stat = os.path.join(PROBLEM_PATH, "problem_zh.md").replace("\\", "/")
        monaco.SimpleFileEditorDialog("???????????????", stat, self)

    def editJudgingConfigure(self):
        global PROBLEM_PATH
        stat = os.path.join(PROBLEM_PATH, "testdata/config.yaml").replace("\\", "/")
        monaco.SimpleFileEditorDialog("?????????????????????", stat, self)

    def editProblemConfigure(self):
        global PROBLEM_PATH
        stat = os.path.join(PROBLEM_PATH, "problem.yaml").replace("\\", "/")
        monaco.SimpleFileEditorDialog("?????????????????????", stat, self)

    def openExampleProblem(self):
        examples = os.listdir("examples")
        choice = QtWidgets.QInputDialog.getItem(self, "Hello Judger", "????????????????????????????????????", examples)
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
        dlg.setWindowTitle("Hello Judger ?????????????????????")
        dlg.show()
        dlg.exec()
    
    def showLinense(self):
        dlg = QtWidgets.QDialog(self)
        dlg.Layout = QtWidgets.QVBoxLayout()
        dlg.widget = markdown_view.MarkdownView()
        dlg.widget.page().loadFinished.connect(lambda: dlg.widget.setValue(LICENSE))
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
        dlg = QtWidgets.QProgressDialog("????????????", "??????", 0, len(need_remove), parent=self)
        dlg.open()
        dlg.setWindowTitle("Hello Judger")
        cleaned = 0
        for i in range(1, len(need_remove)+1):
            if dlg.wasCanceled():
                dlg.close()
                QtWidgets.QMessageBox.critical(self, "Hello Judger", "?????????????????????")
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
        QtWidgets.QMessageBox.information(self, "Hello Judger", "???????????????????????? %d ??????????????????" % (cleaned))

    def OJSearch(self):
        global PROBLEM_PATH
        try:
            with open(os.path.join(PROBLEM_PATH, "problem_zh.md").replace("\\", "/"), encoding="utf-8") as f:
                md = f.read()
        except:
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "??????????????????")
            return
        oj_searcher.OJSearcherDialog(md, self)

    def loadFromHydro(self):
        uuid = str(__import__("uuid").uuid4())
        QtWidgets.QMessageBox.information(self, "Hello Judger", "??????????????? Hydro ????????????????????????\n?????? Hello Judger ?????????????????? Hydro??????????????????????????????????????????????????????????????????????????????????????????\n??????????????????????????????????????????????????????????????????????????????????????????")
        zipfile = QtWidgets.QFileDialog.getOpenFileName(self, "?????? Hydro ??????????????? - Hello Judger")[0]
        if zipfile.strip().rstrip() == "":
            return
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "?????????????????? - Hello Judger")
        if directory.strip().rstrip() == "":
            return
        fobj = ZipFile(zipfile)
        dlg = QtWidgets.QProgressDialog("?????????????????????", "??????", 0, len(fobj.namelist()))
        dlg.setWindowTitle("Hello Judger")
        dlg.open()
        folder = ""
        for i in fobj.namelist():
            folder = i.split('/')[0]
            if dlg.wasCanceled():
                QtWidgets.QMessageBox.critical(self, "Hello Judger", "????????????????????????")
                return
            fobj.extract(i, directory)
            dlg.setValue(dlg.value() + 1)
            QApplication.processEvents()
        dlg.setValue(len(fobj.namelist()))
        dlg.close()
        QtWidgets.QMessageBox.information(self, "Hello Judger", "???????????????")
        self.openProblem(False, os.path.join(directory,folder).replace("\\", "/"))
    
    def independentEditor(self):
        def _(content):
            editor = monaco.SimpleMonacoEditorDialog("???????????????", value=content)
            def __(content):
                self.code_editor.setValue(content)
                editor.close()
            editor.saved.connect(__)
            editor.canceled.connect(editor.close)
            editor.show()
        self.code_editor.getValue(_)


if __name__ == "__main__":
    qdarktheme.enable_hi_dpi()
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(True)
    app.setFont(QtGui.QFont(["Microsoft YaHei", "SimHei", "SimSun"]))
    qdarktheme.setup_theme(theme)
    QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    win = HelloJudgerWindow()
    win.show()
    exit(app.exec())
