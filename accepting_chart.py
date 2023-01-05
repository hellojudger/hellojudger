from PyQt6 import QtWidgets, QtCharts, QtGui


class AcceptingChart(QtCharts.QChartView):
    def __init__(self, total, accept, parent=None):
        series = QtCharts.QPieSeries()
        series.append("Accepted(%d)" % accept, accept)
        series.append("Unaccepted(%d)" % (total-accept), total-accept)

        slice0 = QtCharts.QPieSlice()
        slice0 = series.slices()[0]
        slice0.setLabelVisible(True)
        slice0.setColor(QtGui.QColor("green"))

        slice1 = QtCharts.QPieSlice()
        slice1 = series.slices()[1]
        slice1.setLabelVisible(True)
        slice1.setColor(QtGui.QColor("red"))

        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setTitle("<h2>通过量统计</h2>")
        chart.legend().setVisible(True)
        super().__init__(chart, parent)

# app = QtWidgets.QApplication([])
# win = AcceptingChart(2197, 957)
# win.show()
# app.exec()
