import os
import numpy as np
from scipy import optimize as opt
from PyQt5 import QtWidgets, QtGui

from plot_classes.color_plot import ColorPlot
from helper_classes.mat_file import MatFile
from helper_classes.stack import Stack
from user_interfaces.minmax_dialog import MinMaxDialog
from utility.config import paths
from utility.utility_functions import two_d_gaussian_sym


# noinspection PyAttributeOutsideInit
# noinspection PyArgumentList
class MatWidget(QtWidgets.QWidget):
    def __init__(self, logger, parent=None):
        super(MatWidget, self).__init__(parent)
        self.logger = logger
        try:
            self.parent().mat_is_open = True
        except AttributeError:
            self.logger.add_to_log("Could not set flag.")
        self.pick_stack = Stack()

        back_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'back.png')),
                                     'Back', self)
        back_btn.triggered.connect(self.file_back)
        forward_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'forward.png')),
                                        'Forward', self)
        forward_btn.triggered.connect(self.file_forward)
        open_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'open.png')),
                                     'Open mat', self)
        open_btn.triggered.connect(self.file_open)
        minmax_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join(paths['icons'], 'minmax.png')),
                                       'Set minimum and maximum counts', self)
        minmax_btn.triggered.connect(self.set_minmax)

        self.toolbar = QtWidgets.QToolBar("Image")
        self.toolbar.addAction(back_btn)
        self.toolbar.addAction(forward_btn)
        self.toolbar.addAction(open_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(minmax_btn)

        self.canvas = ColorPlot(self)
        self.canvas.mpl_connect('button_release_event', self.mouse_released)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)
        self.setLayout(vbox)

        self.mat_file = MatFile()
        self.mat_file.load(self, dialog=True)
        self.canvas.draw_canvas(mat=self.mat_file)
        self.logger.add_to_log("Loaded file " + self.mat_file.file_name)

    def file_back(self):
        if self.mat_file.file_name:
            dirname = os.path.dirname(self.mat_file.file_name)
            fname = os.path.basename(self.mat_file.file_name)
            dir_content = [f for f in os.listdir(dirname) if f.endswith('.mat')]
            fname = dir_content[(dir_content.index(fname) - 1 + len(dir_content)) % len(dir_content)]
            self.mat_file.load(self, file_name=os.path.join(dirname, fname))
            self.canvas.draw_canvas(mat=self.mat_file, markers=self.pick_stack.items)
            self.logger.add_to_log("Loaded file " + self.mat_file.file_name)

    def file_forward(self):
        if self.mat_file.file_name:
            dirname = os.path.dirname(self.mat_file.file_name)
            fname = os.path.basename(self.mat_file.file_name)
            dir_content = [f for f in os.listdir(dirname) if f.endswith('.mat')]
            fname = dir_content[(dir_content.index(fname) + 1 + len(dir_content)) % len(dir_content)]
            self.mat_file.load(self, file_name=os.path.join(dirname, fname))
            self.canvas.draw_canvas(mat=self.mat_file, markers=self.pick_stack.items)
            self.logger.add_to_log("Loaded file " + self.mat_file.file_name)

    def file_open(self):
        self.mat_file.load(self, dialog=True)
        self.canvas.draw_canvas(mat=self.mat_file, markers=self.pick_stack.items)
        self.logger.add_to_log("Loaded file " + self.mat_file.file_name)

    def set_minmax(self):
        self.canvas.count_limits_fixed = True
        self.canvas.count_limits = MinMaxDialog(self.canvas.count_limits, self).exec_()
        self.canvas.draw_canvas()

    def mouse_released(self, event):
        if any([event.xdata, event.ydata]):
            if event.button == 1:
                x_ax = self.mat_file.graph['x'][0]
                y_ax = self.mat_file.graph['y'][0][::-1]
                x_ax, y_ax = np.meshgrid(x_ax, y_ax)

                gauss_p0 = (self.canvas.count_limits[1], event.xdata, event.ydata, 0.2,
                            self.canvas.count_limits[0])  # amplitude, x0, y0, sigma, offset
                param_bounds = ([0, event.xdata - 1, event.ydata - 1, 0, -np.inf],
                                [np.inf, event.xdata + 1, event.ydata + 1, np.inf, np.inf])
                popt, _ = opt.curve_fit(two_d_gaussian_sym, [x_ax, y_ax], self.mat_file.graph['result'].ravel(),
                                        p0=gauss_p0, bounds=param_bounds)
                self.pick_stack.push([popt[1], popt[2]])
                self.canvas.draw_canvas(markers=self.pick_stack.items)
            elif event.button == 2:  # manually select point by pressing wheel
                self.pick_stack.push([event.xdata, event.ydata])
                self.canvas.draw_canvas(markers=self.pick_stack.items)
            elif event.button == 3 and not self.pick_stack.is_empty():
                self.pick_stack.pop()
                self.canvas.draw_canvas(markers=self.pick_stack.items)

    def closeEvent(self, event):
        try:
            self.parent().parent().parent().parent().mat_is_open = False
        except AttributeError:
            pass
        event.accept()
