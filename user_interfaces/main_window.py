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

        self.bar = self.menuBar()

        self.file_menu = self.bar.addMenu("File")
        self.file_action_new = self.file_menu.addAction("New")
        self.file_action_open = self.file_menu.addAction("Open")
        self.file_action_open_temp = self.file_menu.addAction("Open Template")
        self.file_action_save = self.file_menu.addAction("Save")
        self.file_action_save_as = self.file_menu.addAction("Save as...")
        self.file_action_import = self.file_menu.addAction("Import")
        self.file_action_export = self.file_menu.addAction("Export")
        # self.file_menu.removeAction(self.file_action_export)
        self.file_menu.triggered[QtWidgets.QAction].connect(self.file_menuaction)

        self.draw_menu = self.bar.addMenu("Draw")
        self.draw_action_line = self.draw_menu.addAction("Line")
        self.draw_action_rectangle = self.draw_menu.addAction("Rectangle")
        self.draw_action_circle = self.draw_menu.addAction("Circle")
        self.draw_action_polyline = self.draw_menu.addAction("Polyline")
        self.draw_action_stencil = self.draw_menu.addAction("Stencil")
        self.draw_menu.triggered[QtWidgets.QAction].connect(self.draw_menuaction)

        self.props_menu = self.bar.addMenu("Properties")
        self.props_action_layer = self.props_menu.addAction("Layer")
        self.props_action_block = self.props_menu.addAction("Block")
        self.props_action_color = self.props_menu.addAction("Color")
        self.props_menu.triggered[QtWidgets.QAction].connect(self.props_menuaction)

        self.view_menu = self.bar.addMenu("View")
        self.view_action_objects = self.view_menu.addAction("View Objects")
        self.view_action_layers = self.view_menu.addAction("View Layers")
        self.view_action_blocks = self.view_menu.addAction("View Blocks")
        self.view_action_grid = self.view_menu.addAction("Show Grid")
        self.view_action_measure = self.view_menu.addAction("Measure")
        self.view_menu.triggered[QtWidgets.QAction].connect(self.view_menuaction)

        self.image_menu = self.bar.addMenu("Image")
        self.image_action_minmax = self.image_menu.addAction("Set Min/Max")
        self.image_action_minmax.setDisabled(True)
        self.image_action_trafo = self.image_menu.addAction("Transform")
        self.image_action_trafo.setDisabled(True)
        self.image_menu.triggered[QtWidgets.QAction].connect(self.image_menuaction)

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

        self.show()

    def file_menuaction(self, q):
        if q.text() == "New":
            self.cad = CADWidget(q.text(), 0, self.logger, self)
            self.cad_widget = QtWidgets.QMdiSubWindow()
            self.cad_widget.setWidget(self.cad)
            self.cad_widget.setWindowTitle("CAD")
            self.cad_widget.setObjectName('WIN_CAD')
            self.mdi.addSubWindow(self.cad_widget)
            self.cad_widget.resize(self.frameGeometry().height() * 3 // 4, self.frameGeometry().height() * 3 // 4)
            self.cad_widget.show()
        elif q.text() == "Open":
            self.cad = CADWidget(q.text(), 0, self.logger, self)
            self.cad_widget = QtWidgets.QMdiSubWindow()
            self.cad_widget.setWidget(self.cad)
            self.cad_widget.setWindowTitle("CAD")
            self.cad_widget.setObjectName('WIN_CAD')
            self.mdi.addSubWindow(self.cad_widget)
            self.cad_widget.resize(self.frameGeometry().height() * 3 // 4, self.frameGeometry().height() * 3 // 4)
            self.cad_widget.show()
        elif q.text() == "Open Template":
            self.cad = CADWidget(q.text(), 0, self.logger, self)
            self.cad_widget = QtWidgets.QMdiSubWindow()
            self.cad_widget.setWidget(self.cad)
            self.cad_widget.setWindowTitle("CAD")
            self.cad_widget.setObjectName('WIN_CAD')
            self.mdi.addSubWindow(self.cad_widget)
            self.cad_widget.resize(self.frameGeometry().height() * 3 // 4, self.frameGeometry().height() * 3 // 4)
            self.cad_widget.show()
        elif q.text() == "Save":
            pass
        elif q.text() == "Save as...":
            pass
        elif q.text() == "Import":
            pass
        elif q.text() == "Export":
            pass

    def draw_menuaction(self, q):  # executes when file menu item selected
        if q.text() == "Line":
            pass
        elif q.text() == "Rectangle":
            pass
        elif q.text() == "Circle":
            pass
        elif q.text() == "Polyline":
            pass
        elif q.text() == "Stencil":
            pass

    def props_menuaction(self, q):  # executes when file menu item selected
        if q.text() == "Layer":
            pass
        elif q.text() == "Block":
            pass
        elif q.text() == "Color":
            pass

    def view_menuaction(self, q):  # executes when file menu item selected
        if q.text() == "View Objects":
            pass
        elif q.text() == "View Layers":
            pass
        elif q.text() == "View Blocks":
            pass
        elif q.text() == "Show Grid":
            pass
        elif q.text() == "Measure":
            pass

    def image_menuaction(self, q):  # executes when file menu item selected
        if q.text() == "Set Min/Max":
            pass
        elif q.text() == "Transform":
            pass
