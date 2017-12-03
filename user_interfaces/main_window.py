import os
from PyQt5 import QtWidgets, QtGui

from user_interfaces.logger import Logger
from user_interfaces.cad_widget import CADWidget
from utility.config import global_confs
from utility.config import paths


# noinspection PyAttributeOutsideInit
# noinspection PyArgumentList
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.init_ui()

    def init_ui(self):

        self.resize(800, 600)
        self.showMaximized()
        self.setWindowIcon(QtGui.QIcon(os.path.join(paths['icons'], 'pykaboo.png')))
        self.setWindowTitle("%s %s" % (global_confs['progname'], global_confs['progversion']))

        self.mdi = QtWidgets.QMdiArea()  # create multiple document interface widget
        self.setCentralWidget(self.mdi)

        self.logger = Logger(self)
        self.log_widget = QtWidgets.QMdiSubWindow()
        self.log_widget.setWidget(self.logger)
        self.log_widget.setWindowTitle("Logger")
        self.log_widget.setObjectName('WIN_LOG')
        self.mdi.addSubWindow(self.log_widget)
        self.log_widget.resize(self.frameGeometry().width(), self.frameGeometry().height()//4)
        self.log_widget.move(0, self.geometry().height()*3//4)
        self.log_widget.show()

        new_dxf_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'new_dxf.png')), 'New dxf', self)
        new_dxf_btn.triggered.connect(self.new_dxf)
        open_dxf_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'open.png')), 'Open dxf', self)
        open_dxf_btn.triggered.connect(self.open_dxf)
        open_temp_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'open_template.png')),
                                          'Open template', self)
        open_temp_btn.triggered.connect(self.open_template)
        save_dxf_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'save.png')), 'Save dxf', self)
        save_dxf_btn.triggered.connect(self.save_dxf)
        save_dxf_as_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'save_as.png')),
                                            'Save dxf as...', self)
        save_dxf_as_btn.triggered.connect(self.save_dxf_as)
        import_mat_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'import.png')), 'Import mat', self)
        import_mat_btn.triggered.connect(self.import_mat)
        export_png_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'export.png')), 'Save png', self)
        export_png_btn.triggered.connect(self.export_png)
        self.toolbar = self.addToolBar("File")
        self.toolbar.addAction(new_dxf_btn)
        self.toolbar.addAction(open_dxf_btn)
        self.toolbar.addAction(open_temp_btn)
        self.toolbar.addAction(save_dxf_btn)
        self.toolbar.addAction(save_dxf_as_btn)
        self.toolbar.addAction(import_mat_btn)
        self.toolbar.addAction(export_png_btn)

        self.show()

    def new_dxf(self):
        self.cad = CADWidget("New", 0, self.logger, self)
        self.cad_widget = QtWidgets.QMdiSubWindow()
        self.cad_widget.setWidget(self.cad)
        self.cad_widget.setWindowTitle("CAD")
        self.cad_widget.setObjectName('WIN_CAD')
        self.mdi.addSubWindow(self.cad_widget)
        self.cad_widget.resize(self.frameGeometry().height() * 3 // 4, self.frameGeometry().height() * 3 // 4)
        self.cad_widget.show()

    def open_dxf(self):
        self.cad = CADWidget("Open", 0, self.logger, self)
        self.cad_widget = QtWidgets.QMdiSubWindow()
        self.cad_widget.setWidget(self.cad)
        self.cad_widget.setWindowTitle("CAD")
        self.cad_widget.setObjectName('WIN_CAD')
        self.mdi.addSubWindow(self.cad_widget)
        self.cad_widget.resize(self.frameGeometry().height() * 3 // 4, self.frameGeometry().height() * 3 // 4)
        self.cad_widget.show()

    def open_template(self):
        self.cad = CADWidget("Open Template", 0, self.logger, self)
        self.cad_widget = QtWidgets.QMdiSubWindow()
        self.cad_widget.setWidget(self.cad)
        self.cad_widget.setWindowTitle("CAD")
        self.cad_widget.setObjectName('WIN_CAD')
        self.mdi.addSubWindow(self.cad_widget)
        self.cad_widget.resize(self.frameGeometry().height() * 3 // 4, self.frameGeometry().height() * 3 // 4)
        self.cad_widget.show()

    def save_dxf(self):
        active_widget = self.mdi.activeSubWindow().widget()
        if isinstance(active_widget, CADWidget):
            active_widget.dxf_file.save(active_widget, overwrite=True)

    def save_dxf_as(self):
        active_widget = self.mdi.activeSubWindow().widget()
        if isinstance(active_widget, CADWidget):
            active_widget.dxf_file.save(active_widget, overwrite=False)

    def import_mat(self):
        pass

    def export_png(self):
        pass
