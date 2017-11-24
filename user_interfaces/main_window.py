from PyQt5 import QtWidgets

from pykaboo5b import progname, progversion
from user_interfaces.nv_localiser import NVLocaliser


class MainWindow(QtWidgets.QMainWindow):
    count = 0  # number of opened windows
    nvloc_isopen = False  # status of NV Localiser widget

    #    log_isopen = False #status of NV Localiser widget

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.mdi = QtWidgets.QMdiArea()  # create multiple document interface widget
        self.setCentralWidget(self.mdi)

        self.bar = self.menuBar()

        task = self.bar.addMenu("Task")  # menu with different tasks (fitting, finding NVs,...)
        task.addAction("NV Localiser")
        task.triggered[QtWidgets.QAction].connect(self.task_windowaction)

        file = self.bar.addMenu("File")  # menu with file tasks (open, load, close, new,...) Currently dummy
        file.addAction("New")
        file.addAction("Cascade")
        file.addAction("Tiled")
        file.triggered[QtWidgets.QAction].connect(self.file_windowaction)

        self.setWindowTitle("%s %s" % (progname, progversion))

    def task_windowaction(self, q):  # executes when task menu item selected

        if q.text() == "NV Localiser":
            if MainWindow.nvloc_isopen == False:  # no nvloc window yet
                MainWindow.count = MainWindow.count + 2
                MainWindow.nvloc_isopen = True

                self.nvloc_widget = QtWidgets.QMdiSubWindow()
                self.nvloc_widget.setWidget(NVLocaliser(self))
                self.nvloc_widget.setWindowTitle("NV Localiser")
                self.nvloc_widget.setObjectName('WIN_NVLOC')
                self.mdi.addSubWindow(self.nvloc_widget)
                self.nvloc_widget.show()

            else:
                pass

        else:
            pass

    def file_windowaction(self, q):  # executes when file menu item selected

        if q.text() == "New":
            MainWindow.count = MainWindow.count + 1
            sub = QtWidgets.QMdiSubWindow()
            sub.setWidget(QtWidgets.QTextEdit())
            sub.setWindowTitle("subwindow" + str(MainWindow.count))
            self.mdi.addSubWindow(sub)
            sub.show()

        elif q.text() == "Cascade":
            self.mdi.cascadeSubWindows()

        elif q.text() == "Tiled":
            self.mdi.tileSubWindows()

        else:
            pass


