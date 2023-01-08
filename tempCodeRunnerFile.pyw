            msg = "评测完成！您通过了这道题，获得了 %.2f 分，恭喜！" % total
        else:
            msg = "评测完成！很遗憾，您获得了 %.2f 分，您没有通过本题。" % total

        QtWidgets.QMessageBox.information(self, "Hello Judger", msg)

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
        try:
            prog = compile.compile_cpp(self.code, self.version, self.optimization)
        except:
            QtWidgets.QMessageBox.critical(self, "Hello Judger", "编译错误")
            self.JUDGING = False
            return
        self.append("编译成功")
        QApplication.processEvents()
        thread = self.JudgingThread(self)
        thread.judge_done.connect(self.judgeDone)
        thread.judge_finished.connect(self.judgeFinished)
        thread.message.connect(self.slot)
        thread.errored.connect(self.errored)