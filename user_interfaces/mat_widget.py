import os
from PyQt5 import QtWidgets, QtGui

from plot_classes.color_plot import ColorPlot
from helper_classes.mat_file import MatFile
from utility.config import paths


# noinspection PyAttributeOutsideInit
class MatWidget(QtWidgets.QWidget):
    def __init__(self, logger, parent=None):
        super(MatWidget, self).__init__(parent)
        self.logger = logger
        try:
            self.parent().mat_is_open = True
        except AttributeError:
            self.logger.add_to_log("Could not set flag.")
            # pass

        back_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'back.png')),
                                     'Back', self)
        back_btn.triggered.connect(self.file_back)
        forward_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'forward.png')),
                                        'Forward', self)
        forward_btn.triggered.connect(self.file_forward)
        open_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'open.png')),
                                     'Open mat', self)
        open_btn.triggered.connect(self.file_open)

        self.toolbar = QtWidgets.QToolBar("Image")
        self.toolbar.addAction(back_btn)
        self.toolbar.addAction(forward_btn)
        self.toolbar.addAction(open_btn)

        self.canvas = ColorPlot(self)
        self.canvas.mpl_connect('button_release_event', self.mouse_released)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)

        self.mat_file = MatFile()
        self.mat_file.load(self)
        self.canvas.draw_canvas(mat=self.mat_file)
        self.logger.add_to_log("New image.")

    def file_back(self):
        pass

    def file_forward(self):
        pass

    def file_open(self):
        pass

    def mouse_released(self, event):
        pass

    def closeEvent(self, event):  # deactivate closing button
        try:
            self.parent().parent().parent().parent().mat_is_open = False
        except AttributeError:
            pass
        event.accept()
