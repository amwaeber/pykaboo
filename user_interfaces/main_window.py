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
        # self.file_menu.removeAction(self.file_action_export)

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
        pass

    def save_dxf_as(self):
        pass

    def import_mat(self):
        pass

    def export_png(self):
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
